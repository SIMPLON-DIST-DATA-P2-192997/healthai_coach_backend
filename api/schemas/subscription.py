from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

SelfServiceTier = Literal["free", "premium", "premium_plus"]
Tier = Literal["free", "premium", "premium_plus", "b2b"]
SubscriptionStatus = Literal["active", "cancelled", "expired"]


class SubscriptionSubscribe(BaseModel):
    """Body for the self-service subscribe/change-tier endpoint.

    `b2b` is intentionally excluded: it requires an `organization_id`, which is
    only assignable by an admin (cf. SubscriptionB2BCreate).
    """
    tier: SelfServiceTier


class SubscriptionB2BCreate(BaseModel):
    """Body for admin-provisioned B2B subscriptions, tied to an organization."""
    user_id: int
    price_eur_cents: int | None = Field(default=None, ge=0)


class SubscriptionRead(BaseModel):
    id: int
    user_id: int
    organization_id: int | None = None
    tier: Tier
    status: SubscriptionStatus
    price_eur_cents: int | None = None
    started_at: datetime
    ended_at: datetime | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
