from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Numeric, String

from api.database import Base


class DietRecommendation(Base):
    __tablename__ = "diet_recommendations"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    daily_caloric_intake_kcal = Column(Numeric(8, 2), nullable=True)
    adherence_to_diet_plan_pct = Column(Numeric(5, 2), nullable=True)
    dietary_nutrient_imbalance_score = Column(Numeric(5, 2), nullable=True)
    recommendation = Column(String, nullable=True)
    recommended_at = Column(DateTime(timezone=True), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<DietRecommendation id={self.id} user_id={self.user_id}>"
