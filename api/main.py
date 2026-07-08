from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from api.config import settings
from api.database import Base, engine
from api.routers import admin, auth, users
from api.routers import (
    biometrics,
    data_quality,
    exercises,
    food_items,
    health_profiles,
    nutrition_logs,
    organizations,
    subscriptions,
    workouts,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Create tables automatically in development.
    # In production, use Alembic migrations instead.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(users.router, prefix=settings.API_PREFIX)
app.include_router(admin.router, prefix=settings.API_PREFIX)
app.include_router(food_items.router, prefix=settings.API_PREFIX)
app.include_router(nutrition_logs.router, prefix=settings.API_PREFIX)
app.include_router(exercises.router, prefix=settings.API_PREFIX)
app.include_router(workouts.router, prefix=settings.API_PREFIX)
app.include_router(biometrics.router, prefix=settings.API_PREFIX)
app.include_router(health_profiles.router, prefix=settings.API_PREFIX)
app.include_router(data_quality.router, prefix=settings.API_PREFIX)
app.include_router(subscriptions.router, prefix=settings.API_PREFIX)
app.include_router(organizations.router, prefix=settings.API_PREFIX)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "version": settings.VERSION}
