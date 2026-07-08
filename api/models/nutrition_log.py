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


class NutritionLog(Base):
    __tablename__ = "nutrition_logs"
    __table_args__ = (
        CheckConstraint("quantity_g > 0", name="ck_nutrition_logs_quantity_g"),
        CheckConstraint(
            "meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')",
            name="ck_nutrition_logs_meal_type",
        ),
    )

    id = Column("log_id", BigInteger().with_variant(Integer, "sqlite"), primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    food_item_id = Column(
        Integer, ForeignKey("food_items.food_item_id", ondelete="RESTRICT"), nullable=False
    )
    quantity_g = Column(Numeric(6, 2), nullable=False)
    meal_type = Column(String(20), nullable=False)
    logged_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<NutritionLog id={self.id} user_id={self.user_id}>"