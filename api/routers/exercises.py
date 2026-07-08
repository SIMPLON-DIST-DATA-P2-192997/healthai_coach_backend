from typing import List

from fastapi import APIRouter, HTTPException, status

from api.core.deps import CurrentAdmin, DB
from api.crud.exercise import create_exercise, delete_exercise, get_exercise, get_exercises, update_exercise
from api.schemas.exercise import ExerciseCreate, ExerciseRead, ExerciseUpdate

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get(
    "",
    response_model=List[ExerciseRead],
    summary="List exercises",
    description="List the exercise catalog (public). Paginated with `skip`/`limit`.",
)
def list_exercises(skip: int = 0, limit: int = 100, db: DB = ...) -> List[ExerciseRead]:  # type: ignore[assignment]
    return get_exercises(db, skip=skip, limit=limit)  # type: ignore[return-value]


@router.get(
    "/{exercise_id}",
    response_model=ExerciseRead,
    summary="Get an exercise",
    description="Return a single exercise from the catalog (public).",
)
def read_exercise(exercise_id: int, db: DB = ...) -> ExerciseRead:  # type: ignore[assignment]
    exercise = get_exercise(db, exercise_id)
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")
    return exercise  # type: ignore[return-value]


@router.post(
    "",
    response_model=ExerciseRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create an exercise",
    description="Add a new exercise to the catalog (admin only).",
)
def create_exercise_endpoint(exercise_in: ExerciseCreate, db: DB, _: CurrentAdmin) -> ExerciseRead:
    return create_exercise(db, exercise_in)  # type: ignore[return-value]


@router.put(
    "/{exercise_id}",
    response_model=ExerciseRead,
    summary="Update an exercise",
    description="Update an exercise in the catalog (admin only).",
)
def update_exercise_endpoint(
    exercise_id: int, update_data: ExerciseUpdate, db: DB, _: CurrentAdmin
) -> ExerciseRead:
    exercise = get_exercise(db, exercise_id)
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")
    return update_exercise(db, exercise, update_data)  # type: ignore[return-value]


@router.delete(
    "/{exercise_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an exercise",
    description="Delete an exercise from the catalog (admin only). Fails if workout sets still "
    "reference it (ON DELETE RESTRICT).",
)
def delete_exercise_endpoint(exercise_id: int, db: DB, _: CurrentAdmin) -> None:
    if not delete_exercise(db, exercise_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")
