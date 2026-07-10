from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)

from api.database import Base


class DietRecommendation(Base):
    __tablename__ = "diet_recommendations"
    __table_args__ = (
        CheckConstraint(
            "daily_caloric_intake_kcal >= 0",
            name="ck_diet_recommendations_daily_caloric_intake_kcal",
        ),
        CheckConstraint(
            "adherence_to_diet_plan_pct BETWEEN 0 AND 100",
            name="ck_diet_recommendations_adherence_to_diet_plan_pct",
        ),
    )

    id = Column(
        "diet_recommendation_id",
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        index=True,
    )
    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    daily_caloric_intake_kcal = Column(Numeric(7, 2), nullable=True)
    adherence_to_diet_plan_pct = Column(Numeric(5, 2), nullable=True)
    dietary_nutrient_imbalance_score = Column(Numeric(6, 2), nullable=True)
    recommendation = Column(String(50), nullable=True)
    recommended_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<DietRecommendation id={self.id} user_id={self.user_id}>"
