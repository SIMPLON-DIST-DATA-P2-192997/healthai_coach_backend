from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, EmailStr

Sex = Literal["F", "M", "other"]


# ---------------------------------------------------------------------------
# Shared base
# ---------------------------------------------------------------------------

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    date_of_birth: date | None = None
    sex: Sex | None = None


# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------

class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    """Fields a regular user can update on themselves."""
    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: date | None = None
    sex: Sex | None = None
    email: EmailStr | None = None


class UserAdminUpdate(UserUpdate):
    """Extended update available to admins."""
    is_admin: bool | None = None


# ---------------------------------------------------------------------------
# Response body
# ---------------------------------------------------------------------------

class UserRead(UserBase):
    id: int
    is_admin: bool
    created_at: datetime

    model_config = {"from_attributes": True}
