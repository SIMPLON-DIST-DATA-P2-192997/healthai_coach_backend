from datetime import datetime

from pydantic import BaseModel, EmailStr

from api.models.user import UserRole


# ---------------------------------------------------------------------------
# Shared base
# ---------------------------------------------------------------------------

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str | None = None


# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------

class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    """Fields a regular user can update on themselves."""
    full_name: str | None = None
    email: EmailStr | None = None


class UserAdminUpdate(UserUpdate):
    """Extended update available to admins."""
    role: UserRole | None = None
    is_active: bool | None = None


# ---------------------------------------------------------------------------
# Response body
# ---------------------------------------------------------------------------

class UserRead(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
