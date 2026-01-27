from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .models import Priority, TaskStatus, MeetingStatus


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    priority: Priority = Priority.Normal
    tags: List[str] = Field(default_factory=list)
    due_date: Optional[date] = None
    status: TaskStatus = TaskStatus.pending


class TaskCreate(TaskBase):
    status: TaskStatus = TaskStatus.pending


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    priority: Optional[Priority] = None
    tags: Optional[List[str]] = None
    due_date: Optional[date] = None
    status: Optional[TaskStatus] = None


class TaskRead(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EventBase(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime
    location: str | None = None
    source: str | None = None
    is_event_day: bool = False
    is_off_day: bool = False


class EventCreate(EventBase):
    pass


class EventRead(EventBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BriefingSection(BaseModel):
    title: str
    items: list[str]


class BriefingResponse(BaseModel):
    day: str
    mode: str
    is_off_day: bool
    off_day_suspected: bool
    agenda: list[BriefingSection]
    plan_summary: list[str]
    top_vip: list[str]
    dogs: list[str]
    house: list[str]


class PlanBlock(BaseModel):
    label: str
    focus: str
    reason: str
    blocks: list[str]


class PlanTodayResponse(BaseModel):
    date: str
    suggestion: str
    plans: list[PlanBlock]


class MeetingUploadResponse(BaseModel):
    id: int
    status: MeetingStatus


class MeetingRead(BaseModel):
    id: int
    title: str
    source: Optional[str] = None
    status: MeetingStatus
    transcript: Optional[str] = None
    summary: Optional[str] = None
    action_items: Optional[list[str]] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
