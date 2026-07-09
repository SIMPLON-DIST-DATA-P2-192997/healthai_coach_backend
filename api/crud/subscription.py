from datetime import datetime, timezone
from typing import List

from sqlalchemy.orm import Session

from api.models.subscription import Subscription

# Public prices for the self-service tiers (cf. database/schema/modele_donnees.md).
# `b2b` has no fixed price: it's negotiated per organization and supplied by an admin.
TIER_PRICES_EUR_CENTS = {"free": 0, "premium": 999, "premium_plus": 1999}


def get_subscription(db: Session, subscription_id: int) -> Subscription | None:
    return db.query(Subscription).filter(Subscription.id == subscription_id).first()


def get_subscriptions_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Subscription]:
    return (
        db.query(Subscription)
        .filter(Subscription.user_id == user_id)
        .order_by(Subscription.started_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_active_subscription(db: Session, user_id: int) -> Subscription | None:
    return (
        db.query(Subscription)
        .filter(Subscription.user_id == user_id, Subscription.status == "active")
        .first()
    )


def _close_active_subscription(db: Session, user_id: int) -> None:
    active = get_active_subscription(db, user_id)
    if active is not None:
        active.status = "cancelled"
        active.ended_at = datetime.now(timezone.utc)
        db.commit()


def create_free_subscription(db: Session, user_id: int) -> Subscription:
    """Create the baseline freemium subscription. Called on user registration and
    whenever a paid subscription is cancelled (downgrade to free rather than to
    no subscription at all)."""
    sub = Subscription(
        user_id=user_id,
        tier="free",
        status="active",
        price_eur_cents=TIER_PRICES_EUR_CENTS["free"],
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


def subscribe(db: Session, user_id: int, tier: str) -> Subscription:
    """Self-service subscribe/change-tier: closes the current active subscription
    (if any) and opens a new one at the requested tier."""
    _close_active_subscription(db, user_id)
    sub = Subscription(
        user_id=user_id,
        tier=tier,
        status="active",
        price_eur_cents=TIER_PRICES_EUR_CENTS[tier],
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


def cancel_active_subscription(db: Session, user_id: int) -> Subscription | None:
    """Cancel the current active subscription and fall back to `free`. Returns
    the new free subscription, or None if the user had no active subscription."""
    active = get_active_subscription(db, user_id)
    if active is None:
        return None
    if active.tier == "free":
        return active
    _close_active_subscription(db, user_id)
    return create_free_subscription(db, user_id)


def create_b2b_subscription(
    db: Session, user_id: int, organization_id: int, price_eur_cents: int | None
) -> Subscription:
    """Admin-provisioned B2B subscription, tied to an organization."""
    _close_active_subscription(db, user_id)
    sub = Subscription(
        user_id=user_id,
        organization_id=organization_id,
        tier="b2b",
        status="active",
        price_eur_cents=price_eur_cents,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub
