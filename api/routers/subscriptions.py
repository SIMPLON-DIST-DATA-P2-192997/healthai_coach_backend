from typing import List

from fastapi import APIRouter, HTTPException, status

from api.core.deps import CurrentUser, DB
from api.crud.subscription import (
    cancel_active_subscription, get_active_subscription, get_subscriptions_by_user, subscribe,
)
from api.schemas.subscription import SubscriptionRead, SubscriptionSubscribe

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get(
    "",
    response_model=List[SubscriptionRead],
    summary="List my subscription history",
    description="Return the authenticated user's subscription history (tier changes, "
    "cancellations), most recent first.",
)
def list_my_subscriptions(
    skip: int = 0, limit: int = 100,
    current_user: CurrentUser = ...,  # type: ignore[assignment]
    db: DB = ...,  # type: ignore[assignment]
) -> List[SubscriptionRead]:
    return get_subscriptions_by_user(db, current_user.id, skip=skip, limit=limit)  # type: ignore[return-value]


@router.get(
    "/current",
    response_model=SubscriptionRead,
    summary="Get my current subscription",
    description="Return the authenticated user's currently active subscription.",
)
def read_my_current_subscription(current_user: CurrentUser, db: DB) -> SubscriptionRead:
    sub = get_active_subscription(db, current_user.id)
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active subscription")
    return sub  # type: ignore[return-value]


@router.post(
    "",
    response_model=SubscriptionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Subscribe or change tier",
    description="Subscribe the authenticated user to a tier (free, premium, premium_plus). "
    "Closes the current active subscription, if any, and opens a new one. `b2b` is not "
    "self-service — it requires an organization and is provisioned by an admin (see "
    "POST /organizations/{organization_id}/subscriptions). No payment is processed by this "
    "endpoint; `price_eur_cents` on the created record is informational only.",
)
def subscribe_endpoint(
    data_in: SubscriptionSubscribe, current_user: CurrentUser, db: DB
) -> SubscriptionRead:
    return subscribe(db, current_user.id, data_in.tier)  # type: ignore[return-value]


@router.delete(
    "/current",
    response_model=SubscriptionRead,
    summary="Cancel my current subscription",
    description="Cancel the authenticated user's currently active subscription and fall back "
    "to the free tier.",
)
def cancel_my_subscription(current_user: CurrentUser, db: DB) -> SubscriptionRead:
    sub = cancel_active_subscription(db, current_user.id)
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active subscription")
    return sub  # type: ignore[return-value]
