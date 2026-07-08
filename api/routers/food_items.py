from typing import List

from fastapi import APIRouter, HTTPException, status

from api.core.deps import CurrentAdmin, DB
from api.crud.food_item import create_food_item, delete_food_item, get_food_item, get_food_items, update_food_item
from api.schemas.food_item import FoodItemCreate, FoodItemRead, FoodItemUpdate

router = APIRouter(prefix="/food-items", tags=["food-items"])


@router.get("", response_model=List[FoodItemRead])
def list_food_items(skip: int = 0, limit: int = 100, db: DB = ...) -> List[FoodItemRead]:  # type: ignore[assignment]
    return get_food_items(db, skip=skip, limit=limit)  # type: ignore[return-value]


@router.get("/{food_item_id}", response_model=FoodItemRead)
def read_food_item(food_item_id: int, db: DB = ...) -> FoodItemRead:  # type: ignore[assignment]
    item = get_food_item(db, food_item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food item not found")
    return item  # type: ignore[return-value]


@router.post("", response_model=FoodItemRead, status_code=status.HTTP_201_CREATED)
def create_food_item_endpoint(
    item_in: FoodItemCreate,
    db: DB,
    _: CurrentAdmin,
) -> FoodItemRead:
    return create_food_item(db, item_in)  # type: ignore[return-value]


@router.put("/{food_item_id}", response_model=FoodItemRead)
def update_food_item_endpoint(
    food_item_id: int,
    update_data: FoodItemUpdate,
    db: DB,
    _: CurrentAdmin,
) -> FoodItemRead:
    item = get_food_item(db, food_item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food item not found")
    return update_food_item(db, item, update_data)  # type: ignore[return-value]


@router.delete("/{food_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_food_item_endpoint(food_item_id: int, db: DB, _: CurrentAdmin) -> None:
    if not delete_food_item(db, food_item_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food item not found")
