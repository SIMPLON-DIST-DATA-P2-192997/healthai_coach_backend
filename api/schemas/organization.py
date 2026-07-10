from datetime import datetime

from pydantic import BaseModel, EmailStr


class OrganizationBase(BaseModel):
    name: str
    contact_email: EmailStr


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: str | None = None
    contact_email: EmailStr | None = None


class OrganizationRead(OrganizationBase):
    id: int
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
