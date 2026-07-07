from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String

from api.database import Base


class DietaryPreference(Base):
    __tablename__ = "dietary_preferences"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    dietary_restrictions = Column(String, nullable=True)
    allergies = Column(String, nullable=True)
    preferred_cuisine = Column(String, nullable=True)
    recorded_at = Column(DateTime(timezone=True), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<DietaryPreference id={self.id} user_id={self.user_id}>"
