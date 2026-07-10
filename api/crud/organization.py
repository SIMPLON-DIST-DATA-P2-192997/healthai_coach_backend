from typing import List

from sqlalchemy.orm import Session

from api.models.organization import Organization
from api.schemas.organization import OrganizationCreate, OrganizationUpdate


def get_organization(db: Session, organization_id: int) -> Organization | None:
    return db.query(Organization).filter(Organization.id == organization_id).first()


def get_organizations(db: Session, skip: int = 0, limit: int = 100) -> List[Organization]:
    return db.query(Organization).offset(skip).limit(limit).all()


def create_organization(db: Session, org_in: OrganizationCreate) -> Organization:
    org = Organization(**org_in.model_dump())
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


def update_organization(db: Session, org: Organization, update_data: OrganizationUpdate) -> Organization:
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(org, field, value)
    db.commit()
    db.refresh(org)
    return org
