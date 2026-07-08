from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, func

from api.database import Base


class DietaryPreference(Base):
    __tablename__ = "dietary_preferences"

    id = Column(
        "dietary_preference_id",
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        index=True,
    )
    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    dietary_restrictions = Column(String(255), nullable=True)
    allergies = Column(String(255), nullable=True)
    preferred_cuisine = Column(String(100), nullable=True)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<DietaryPreference id={self.id} user_id={self.user_id}>"
