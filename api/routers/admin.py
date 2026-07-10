from typing import List

from fastapi import APIRouter, HTTPException, status

from api.core.deps import CurrentAdmin, DB
from api.crud.user import delete_user, get_user, get_users, update_user
from api.schemas.user import UserAdminUpdate, UserRead

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=List[UserRead], summary="List all users")
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: DB = ...,  # type: ignore[assignment]
    _: CurrentAdmin = ...,  # type: ignore[assignment]
) -> List[UserRead]:
    """List all users (admin only)."""
    return get_users(db, skip=skip, limit=limit)  # type: ignore[return-value]


@router.get("/users/{user_id}", response_model=UserRead, summary="Get a user")
def read_user(
    user_id: int,
    db: DB,
    _: CurrentAdmin,
) -> UserRead:
    """Get a specific user by ID (admin only)."""
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user  # type: ignore[return-value]


@router.put("/users/{user_id}", response_model=UserRead, summary="Update a user")
def update_user_admin(
    user_id: int,
    update_data: UserAdminUpdate,
    db: DB,
    _: CurrentAdmin,
) -> UserRead:
    """Update any user's data or role (admin only)."""
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return update_user(db, user, update_data)  # type: ignore[return-value]


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a user")
def delete_user_admin(
    user_id: int,
    db: DB,
    _: CurrentAdmin,
) -> None:
    """Delete a user (admin only)."""
    if not delete_user(db, user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
