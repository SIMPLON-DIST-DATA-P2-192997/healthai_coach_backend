from pydantic import BaseModel


class AIGenerationRequest(BaseModel):
    """Shared request body for the /ai/* generation endpoints."""
    goal: str | None = None
