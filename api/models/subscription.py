from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
    text,
)

from api.database import Base


class Subscription(Base):
    __tablename__ = "subscriptions"
    __table_args__ = (
        CheckConstraint(
            "tier IN ('free', 'premium', 'premium_plus', 'b2b')", name="ck_subscriptions_tier"
        ),
        CheckConstraint(
            "status IN ('active', 'cancelled', 'expired')", name="ck_subscriptions_status"
        ),
        CheckConstraint("price_eur_cents >= 0", name="ck_subscriptions_price_eur_cents"),
        CheckConstraint(
            "ended_at IS NULL OR ended_at >= started_at",
            name="chk_subscriptions_ended_after_started",
        ),
        CheckConstraint(
            "(tier = 'b2b' AND organization_id IS NOT NULL) "
            "OR (tier <> 'b2b' AND organization_id IS NULL)",
            name="chk_subscriptions_b2b_organization",
        ),
        Index(
            "uq_subscriptions_one_active_per_user",
            "user_id",
            unique=True,
            postgresql_where=text("status = 'active'"),
            sqlite_where=text("status = 'active'"),
        ),
    )

    id = Column(
        "subscription_id", BigInteger().with_variant(Integer, "sqlite"), primary_key=True, index=True
    )
    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    organization_id = Column(
        Integer, ForeignKey("organizations.organization_id", ondelete="RESTRICT"), nullable=True
    )
    tier = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, server_default=text("'active'"))
    price_eur_cents = Column(Integer, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<Subscription id={self.id} user_id={self.user_id} tier={self.tier!r} status={self.status!r}>"
