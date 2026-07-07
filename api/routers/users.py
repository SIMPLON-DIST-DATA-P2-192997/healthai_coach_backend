from fastapi import APIRouter, HTTPException, status

from api.core.deps import CurrentUser, DB
from api.crud.user import update_user
from api.schemas.user import UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: CurrentUser) -> UserRead:
    """Return the currently authenticated user's profile."""
    return current_user  # type: ignore[return-value]


@router.put("/me", response_model=UserRead)
def update_current_user(
    update_data: UserUpdate,
    current_user: CurrentUser,
    db: DB,
) -> UserRead:
    """Update the currently authenticated user's own profile."""
    return update_user(db, current_user, update_data)  # type: ignore[return-value]
