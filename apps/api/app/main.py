from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import Base, engine, get_session
from app.routers import briefing, calendar, health, plan, tasks, meetings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # For local dev convenience (tests handle schema separately)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # No teardown needed for now


def create_app() -> FastAPI:
    app = FastAPI(title="WALL-E API", version="0.1.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(tasks.router)
    app.include_router(calendar.router)
    app.include_router(briefing.router)
    app.include_router(plan.router)
    app.include_router(meetings.router)

    return app


app = create_app()

# Re-export for tests
__all__ = ["app", "get_session"]
