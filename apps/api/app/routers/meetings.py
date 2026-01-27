import os
from pathlib import Path
from typing import Callable

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app import crud
from app.models import MeetingStatus
from app.schemas import MeetingUploadResponse, MeetingRead, TaskCreate
from app.services import transcribe as transcribe_service
from app.services.gemini_client import GeminiUnavailable

UPLOAD_DIR = Path("temp/meetings")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter(prefix="/meetings", tags=["meetings"])


def get_transcriber() -> Callable:
    return transcribe_service.transcribe_and_summarize


@router.post("/upload", response_model=MeetingUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_meeting(
    title: str = Form(...),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    if file.content_type not in {"audio/wav", "audio/mpeg", "audio/mp3", "audio/mp4", "audio/webm"}:
        raise HTTPException(status_code=400, detail="Formato no soportado")
    filename = f"{file.filename or 'audio'}.{file.content_type.split('/')[-1]}"
    filepath = UPLOAD_DIR / filename
    data = await file.read()
    filepath.write_bytes(data)
    meeting = await crud.create_meeting_audio(session, title=title, source="upload", file_path=str(filepath))
    return MeetingUploadResponse(id=meeting.id, status=meeting.status)


@router.post("/{meeting_id}/process", response_model=MeetingRead)
async def process_meeting(
    meeting_id: int,
    session: AsyncSession = Depends(get_session),
    transcriber: Callable = Depends(get_transcriber),
):
    meeting = await crud.get_meeting_audio(session, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting no encontrado")
    try:
        transcript, summary, action_items = await transcriber(session, meeting)
        meeting = await crud.update_meeting_audio(
            session,
            meeting,
            status=MeetingStatus.transcribed,
            transcript=transcript,
            summary=summary,
            action_items=action_items,
            error=None,
        )
    except GeminiUnavailable as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:  # noqa: BLE001
        meeting = await crud.update_meeting_audio(
            session, meeting, status=MeetingStatus.failed, error=str(e)
        )
        raise HTTPException(status_code=500, detail="Error al transcribir")
    return meeting


@router.get("/{meeting_id}", response_model=MeetingRead)
async def get_meeting(meeting_id: int, session: AsyncSession = Depends(get_session)):
    meeting = await crud.get_meeting_audio(session, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting no encontrado")
    return meeting


@router.get("", response_model=list[MeetingRead])
async def list_meetings(session: AsyncSession = Depends(get_session)):
    return await crud.list_meeting_audios(session)


@router.post("/{meeting_id}/export-tasks", response_model=list[dict])
async def export_tasks(meeting_id: int, session: AsyncSession = Depends(get_session)):
    meeting = await crud.get_meeting_audio(session, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting no encontrado")
    if not meeting.action_items:
        raise HTTPException(status_code=400, detail="No hay action items")
    created = []
    for item in meeting.action_items:
        task = await crud.create_task(session, payload=TaskCreate(title=item, priority="Important", tags=["work"]))
        created.append({"id": task.id, "title": task.title})
    return created
