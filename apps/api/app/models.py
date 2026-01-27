import enum

from sqlalchemy import JSON, Boolean, Column, Date, DateTime, Enum, Integer, String, func

from .db import Base


class Priority(str, enum.Enum):
    VIP = "VIP"
    Important = "Important"
    Normal = "Normal"


class TaskStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    done = "done"

class MeetingStatus(str, enum.Enum):
    pending = "pending"
    transcribed = "transcribed"
    failed = "failed"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    priority = Column(Enum(Priority), nullable=False, default=Priority.Normal)
    tags = Column(JSON, default=list)
    due_date = Column(Date, nullable=True)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location = Column(String(255), nullable=True)
    source = Column(String(50), nullable=True)  # e.g. mock/google
    is_event_day = Column(Boolean, default=False)
    is_off_day = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class OffDay(Base):
    __tablename__ = "off_days"

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False, unique=True)
    reason = Column(String(255), nullable=True)


class MeetingAudio(Base):
    __tablename__ = "meeting_audios"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    source = Column(String(50), nullable=True)  # e.g. upload/mic/link
    file_path = Column(String(512), nullable=False)
    status = Column(Enum(MeetingStatus), nullable=False, default=MeetingStatus.pending)
    transcript = Column(String, nullable=True)
    summary = Column(String, nullable=True)
    action_items = Column(JSON, nullable=True)
    error = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
