from typing import List

from fastapi import APIRouter, HTTPException, status

from api.core.deps import CurrentUser, DB
from api.crud.nutrition_log import (
    create_nutrition_log, delete_nutrition_log,
    get_nutrition_log, get_nutrition_logs_by_user, update_nutrition_log,
)
from api.schemas.nutrition_log import NutritionLogCreate, NutritionLogRead, NutritionLogUpdate

router = APIRouter(prefix="/nutrition-logs", tags=["nutrition-logs"])


@router.get(
    "",
    response_model=List[NutritionLogRead],
    summary="List my nutrition logs",
    description="Return the authenticated user's logged meals, most recent first.",
)
def list_my_nutrition_logs(
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = ...,  # type: ignore[assignment]
    db: DB = ...,  # type: ignore[assignment]
) -> List[NutritionLogRead]:
    return get_nutrition_logs_by_user(db, current_user.id, skip=skip, limit=limit)  # type: ignore[return-value]


@router.get(
    "/{log_id}",
    response_model=NutritionLogRead,
    summary="Get a nutrition log",
    description="Return a single logged meal owned by the authenticated user.",
)
def read_nutrition_log(log_id: int, current_user: CurrentUser, db: DB) -> NutritionLogRead:
    log = get_nutrition_log(db, log_id)
    if not log or int(log.user_id) != current_user.id:  # type: ignore[arg-type]
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")
    return log  # type: ignore[return-value]


@router.post(
    "",
    response_model=NutritionLogRead,
    status_code=status.HTTP_201_CREATED,
    summary="Log a meal",
    description="Record that the authenticated user consumed a given quantity of a food item. "
    "`meal_type` must be one of breakfast, lunch, dinner, snack. Defaults `logged_at` to now if "
    "omitted.",
)
def create_my_nutrition_log(
    log_in: NutritionLogCreate,
    current_user: CurrentUser,
    db: DB,
) -> NutritionLogRead:
    return create_nutrition_log(db, current_user.id, log_in)  # type: ignore[return-value]


@router.put(
    "/{log_id}",
    response_model=NutritionLogRead,
    summary="Update a nutrition log",
    description="Partially update a logged meal owned by the authenticated user.",
)
def update_my_nutrition_log(
    log_id: int,
    update_data: NutritionLogUpdate,
    current_user: CurrentUser,
    db: DB,
) -> NutritionLogRead:
    log = get_nutrition_log(db, log_id)
    if not log or int(log.user_id) != current_user.id:  # type: ignore[arg-type]
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")
    return update_nutrition_log(db, log, update_data)  # type: ignore[return-value]


@router.delete(
    "/{log_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a nutrition log",
    description="Delete a logged meal owned by the authenticated user.",
)
def delete_my_nutrition_log(log_id: int, current_user: CurrentUser, db: DB) -> None:
    log = get_nutrition_log(db, log_id)
    if not log or int(log.user_id) != current_user.id:  # type: ignore[arg-type]
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")
    delete_nutrition_log(db, log_id)
