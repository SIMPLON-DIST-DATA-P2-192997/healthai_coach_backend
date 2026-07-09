from sqlalchemy import CheckConstraint, Column, DateTime, Integer, Numeric, String, UniqueConstraint, func

from api.database import Base


class FoodItem(Base):
    __tablename__ = "food_items"
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_food_items_source_external_id"),
        CheckConstraint("calories_kcal >= 0", name="ck_food_items_calories_kcal"),
        CheckConstraint("protein_g >= 0", name="ck_food_items_protein_g"),
        CheckConstraint("carbs_g >= 0", name="ck_food_items_carbs_g"),
        CheckConstraint("fat_g >= 0", name="ck_food_items_fat_g"),
        CheckConstraint("fiber_g >= 0", name="ck_food_items_fiber_g"),
        CheckConstraint("sugar_g >= 0", name="ck_food_items_sugar_g"),
        CheckConstraint("sodium_mg >= 0", name="ck_food_items_sodium_mg"),
        CheckConstraint("cholesterol_mg >= 0", name="ck_food_items_cholesterol_mg"),
    )

    id = Column("food_item_id", Integer, primary_key=True, index=True)
    external_id = Column(String(100), nullable=True, index=True)
    source = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    brand = Column(String(255), nullable=True)
    category = Column(String(50), nullable=True)
    calories_kcal = Column(Numeric(7, 2), nullable=False)
    protein_g = Column(Numeric(6, 2), nullable=True)
    carbs_g = Column(Numeric(6, 2), nullable=True)
    fat_g = Column(Numeric(6, 2), nullable=True)
    fiber_g = Column(Numeric(6, 2), nullable=True)
    sugar_g = Column(Numeric(6, 2), nullable=True)
    sodium_mg = Column(Numeric(7, 2), nullable=True)
    cholesterol_mg = Column(Numeric(7, 2), nullable=True)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<FoodItem id={self.id} name={self.name!r}>"
