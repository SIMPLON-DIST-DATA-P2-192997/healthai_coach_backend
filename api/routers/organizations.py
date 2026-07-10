from typing import List

from fastapi import APIRouter, HTTPException, status

from api.core.deps import CurrentAdmin, DB
from api.crud.organization import (
    create_organization, get_organization, get_organizations, update_organization,
)
from api.crud.subscription import create_b2b_subscription
from api.crud.user import get_user
from api.schemas.organization import OrganizationCreate, OrganizationRead, OrganizationUpdate
from api.schemas.subscription import SubscriptionB2BCreate, SubscriptionRead

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get(
    "",
    response_model=List[OrganizationRead],
    summary="List organizations",
    description="List B2B partner organizations (salles de sport, mutuelles, entreprises) "
    "(admin only).",
)
def list_organizations(
    skip: int = 0,
    limit: int = 100,
    db: DB = ...,  # type: ignore[assignment]
    _: CurrentAdmin = ...,  # type: ignore[assignment]
) -> List[OrganizationRead]:
    return get_organizations(db, skip=skip, limit=limit)  # type: ignore[return-value]


@router.post(
    "",
    response_model=OrganizationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create an organization",
    description="Onboard a new B2B partner organization for white-label distribution "
    "(admin only).",
)
def create_organization_endpoint(org_in: OrganizationCreate, db: DB, _: CurrentAdmin) -> OrganizationRead:
    return create_organization(db, org_in)  # type: ignore[return-value]


@router.get(
    "/{organization_id}",
    response_model=OrganizationRead,
    summary="Get an organization",
    description="Return a single B2B partner organization (admin only).",
)
def read_organization(organization_id: int, db: DB, _: CurrentAdmin) -> OrganizationRead:
    org = get_organization(db, organization_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return org  # type: ignore[return-value]


@router.put(
    "/{organization_id}",
    response_model=OrganizationRead,
    summary="Update an organization",
    description="Update a B2B partner organization (admin only).",
)
def update_organization_endpoint(
    organization_id: int, update_data: OrganizationUpdate, db: DB, _: CurrentAdmin
) -> OrganizationRead:
    org = get_organization(db, organization_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return update_organization(db, org, update_data)  # type: ignore[return-value]


@router.post(
    "/{organization_id}/subscriptions",
    response_model=SubscriptionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Provision a B2B subscription",
    description="Attach a user to this organization's B2B plan (admin only). Closes the "
    "user's current active subscription, if any. `price_eur_cents` is the negotiated price "
    "for this organization's contract, if known.",
)
def create_b2b_subscription_endpoint(
    organization_id: int, data_in: SubscriptionB2BCreate, db: DB, _: CurrentAdmin
) -> SubscriptionRead:
    org = get_organization(db, organization_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    if not get_user(db, data_in.user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return create_b2b_subscription(  # type: ignore[return-value]
        db, data_in.user_id, organization_id, data_in.price_eur_cents
    )
