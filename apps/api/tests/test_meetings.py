import io
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.main import app, get_session
from app.db import Base
from app import crud
from app.models import MeetingStatus


@pytest.fixture
async def client():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_session():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.mark.asyncio
async def test_upload_meeting(client: AsyncClient):
    audio = io.BytesIO(b"fake-audio")
    files = {"file": ("sample.wav", audio, "audio/wav")}
    data = {"title": "Reunion diaria"}
    res = await client.post("/meetings/upload", files=files, data=data)
    assert res.status_code == 201
    body = res.json()
    assert body["status"] == MeetingStatus.pending.value
    assert "id" in body


@pytest.mark.asyncio
async def test_process_meeting_with_mock(client: AsyncClient, monkeypatch):
    # Upload first
    audio = io.BytesIO(b"fake-audio")
    files = {"file": ("sample.wav", audio, "audio/wav")}
    data = {"title": "Reunion mock"}
    res = await client.post("/meetings/upload", files=files, data=data)
    meeting_id = res.json()["id"]

    async def fake_transcriber(session, meeting):
        return "transcript ok", "summary ok", ["Accion 1", "Accion 2"]

    from app.routers import meetings as meetings_router

    app.dependency_overrides[meetings_router.get_transcriber] = lambda: fake_transcriber

    res_process = await client.post(f"/meetings/{meeting_id}/process")
    assert res_process.status_code == 200
    body = res_process.json()
    assert body["status"] == MeetingStatus.transcribed.value
    assert "Accion 1" in body["action_items"]


@pytest.mark.asyncio
async def test_export_tasks(client: AsyncClient, monkeypatch):
    audio = io.BytesIO(b"fake-audio")
    files = {"file": ("sample.wav", audio, "audio/wav")}
    data = {"title": "Reunion tareas"}
    res = await client.post("/meetings/upload", files=files, data=data)
    meeting_id = res.json()["id"]

    async def fake_transcriber(session, meeting):
        return "t", "s", ["Task one"]

    from app.routers import meetings as meetings_router

    app.dependency_overrides[meetings_router.get_transcriber] = lambda: fake_transcriber
    await client.post(f"/meetings/{meeting_id}/process")

    res_export = await client.post(f"/meetings/{meeting_id}/export-tasks")
    assert res_export.status_code == 200
    tasks = res_export.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Task one"
