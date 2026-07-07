from sqlalchemy import BigInteger, Column, DateTime, Numeric, String, func

from api.database import Base


class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(BigInteger, primary_key=True, index=True)
    external_id = Column(String, nullable=True, index=True)
    source = Column(String, nullable=True)
    name = Column(String, nullable=False)
    brand = Column(String, nullable=True)
    calories_kcal = Column(Numeric(7, 2), nullable=True)
    protein_g = Column(Numeric(7, 2), nullable=True)
    carbs_g = Column(Numeric(7, 2), nullable=True)
    fat_g = Column(Numeric(7, 2), nullable=True)
    fiber_g = Column(Numeric(7, 2), nullable=True)
    sugar_g = Column(Numeric(7, 2), nullable=True)
    sodium_mg = Column(Numeric(7, 2), nullable=True)
    cholesterol_mg = Column(Numeric(7, 2), nullable=True)
    serving_size_g = Column(Numeric(7, 2), nullable=True)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<FoodItem id={self.id} name={self.name!r}>"
