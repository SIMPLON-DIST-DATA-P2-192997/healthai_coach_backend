from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from api.config import settings
from api.database import Base, engine
from api.routers import admin, auth, users
from api.routers import (
    ai,
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

API_DESCRIPTION = """
REST API for HealthAI Coach: user accounts, nutrition logging, workout tracking,
biometrics, health profiles (medical/dietary/fitness) and diet recommendations.

Data model reference: `database/schema/modele_donnees.md` (MCD/MLD) and
`database/schema/ddl_postgres.sql` (MPD) — the physical schema backing these
endpoints.

Authentication: `POST /auth/login` returns a JWT bearer token (OAuth2 password
flow). Send it as `Authorization: Bearer <token>` on subsequent requests.
Most `/health-profiles`, `/nutrition-logs`, `/workouts` and `/biometrics`
endpoints operate on the authenticated user's own data; catalog endpoints
(`/food-items`, `/exercises`) are readable by anyone but writable by admins
only; `/admin` and `/data-quality` are admin-only. `/ai` endpoints require an
active premium/premium_plus/b2b subscription (see `/subscriptions`).
"""

TAGS_METADATA = [
    {"name": "auth", "description": "Registration and login (JWT issuance)."},
    {"name": "users", "description": "The authenticated user's own profile."},
    {
        "name": "admin",
        "description": "Admin-only user management (list/read/update/delete any user).",
    },
    {
        "name": "food-items",
        "description": "Food catalog, fed by the nutrition ETL. Readable by anyone, "
        "writable by admins only.",
    },
    {
        "name": "nutrition-logs",
        "description": "The authenticated user's logged meals (what they ate, when, how much).",
    },
    {
        "name": "exercises",
        "description": "Exercise catalog, fed by the exercises ETL. Readable by anyone, "
        "writable by admins only.",
    },
    {
        "name": "workouts",
        "description": "The authenticated user's workout sessions and the sets performed "
        "within them.",
    },
    {
        "name": "biometrics",
        "description": "The authenticated user's biometric measurements over time (weight, "
        "height, body composition...).",
    },
    {
        "name": "health-profiles",
        "description": "The authenticated user's historized medical profile, dietary "
        "preferences, fitness profile, and read-only diet recommendations.",
    },
    {
        "name": "data-quality",
        "description": "Admin-only view into data quality anomalies detected by the ETL "
        "pipeline, and their resolution.",
    },
    {
        "name": "subscriptions",
        "description": "The authenticated user's subscription (free/premium/premium_plus), "
        "self-service tier changes and cancellation.",
    },
    {
        "name": "organizations",
        "description": "Admin-only B2B partner management and subscription provisioning "
        "(white-label distribution to gyms/mutuelles/entreprises).",
    },
    {
        "name": "ai",
        "description": "AI-generated content (diet recommendations, workout/nutrition plans), "
        "gated to premium/premium_plus/b2b subscribers. The AI microservice isn't deployed yet: "
        "responses are placeholders (see api/services/ai_client.py).",
    },
    {"name": "health", "description": "Service liveness check."},
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Create tables automatically in development.
    # In production, use Alembic migrations instead.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=API_DESCRIPTION,
    openapi_tags=TAGS_METADATA,
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
app.include_router(ai.router, prefix=settings.API_PREFIX)


# ---------------------------------------------------------------------------
# Root & health check
# ---------------------------------------------------------------------------

@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    """Redirect to the interactive API docs."""
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["health"], summary="Health check")
def health_check() -> dict[str, str]:
    return {"status": "ok", "version": settings.VERSION}
