from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, Text, func

from api.database import Base


class NutritionPlan(Base):
    __tablename__ = "nutrition_plans"

    id = Column(
        "nutrition_plan_id", BigInteger().with_variant(Integer, "sqlite"), primary_key=True, index=True
    )
    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    goal = Column(String(255), nullable=True)
    plan_text = Column(Text, nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<NutritionPlan id={self.id} user_id={self.user_id}>"
