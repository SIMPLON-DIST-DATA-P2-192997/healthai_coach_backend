from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Numeric, String, func

from api.database import Base


class NutritionLog(Base):
    __tablename__ = "nutrition_logs"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    food_item_id = Column(BigInteger, ForeignKey("food_items.id", ondelete="RESTRICT"), nullable=False)
    quantity_g = Column(Numeric(7, 2), nullable=False)
    meal_type = Column(String, nullable=True)
    logged_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<NutritionLog id={self.id} user_id={self.user_id}>"
