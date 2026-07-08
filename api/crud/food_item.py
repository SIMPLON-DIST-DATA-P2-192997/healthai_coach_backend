from typing import List

from sqlalchemy.orm import Session

from api.models.food_item import FoodItem
from api.schemas.food_item import FoodItemCreate, FoodItemUpdate


def get_food_item(db: Session, food_item_id: int) -> FoodItem | None:
    return db.query(FoodItem).filter(FoodItem.id == food_item_id).first()


def get_food_items(db: Session, skip: int = 0, limit: int = 100) -> List[FoodItem]:
    return db.query(FoodItem).offset(skip).limit(limit).all()


def create_food_item(db: Session, item_in: FoodItemCreate) -> FoodItem:
    item = FoodItem(**item_in.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_food_item(db: Session, item: FoodItem, update_data: FoodItemUpdate) -> FoodItem:
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


def delete_food_item(db: Session, food_item_id: int) -> bool:
    item = get_food_item(db, food_item_id)
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True
