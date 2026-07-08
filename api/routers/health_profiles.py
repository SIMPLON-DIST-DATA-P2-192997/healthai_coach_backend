from typing import List

from fastapi import APIRouter, HTTPException, status

from api.core.deps import CurrentUser, DB
from api.crud.health_profile import (
    create_dietary_preference,
    create_fitness_profile, create_medical_profile,
    delete_dietary_preference, delete_fitness_profile, delete_medical_profile,
    get_dietary_preference, get_dietary_preferences,
    get_diet_recommendations,
    get_fitness_profile, get_fitness_profiles,
    get_medical_profile, get_medical_profiles,
)
from api.schemas.dietary_preference import DietaryPreferenceCreate, DietaryPreferenceRead
from api.schemas.diet_recommendation import DietRecommendationRead
from api.schemas.fitness_profile import FitnessProfileCreate, FitnessProfileRead
from api.schemas.medical_profile import MedicalProfileCreate, MedicalProfileRead

router = APIRouter(prefix="/health-profiles", tags=["health-profiles"])


# ---------------------------------------------------------------------------
# Medical profiles
# ---------------------------------------------------------------------------

@router.get("/medical", response_model=List[MedicalProfileRead])
def list_medical_profiles(
    skip: int = 0, limit: int = 100,
    current_user: CurrentUser = ...,  # type: ignore[assignment]
    db: DB = ...,  # type: ignore[assignment]
) -> List[MedicalProfileRead]:
    return get_medical_profiles(db, current_user.id, skip=skip, limit=limit)  # type: ignore[return-value]


@router.post("/medical", response_model=MedicalProfileRead, status_code=status.HTTP_201_CREATED)
def create_my_medical_profile(data_in: MedicalProfileCreate, current_user: CurrentUser, db: DB) -> MedicalProfileRead:
    return create_medical_profile(db, current_user.id, data_in)  # type: ignore[return-value]


@router.delete("/medical/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_medical_profile(profile_id: int, current_user: CurrentUser, db: DB) -> None:
    obj = get_medical_profile(db, profile_id)
    if not obj or int(obj.user_id) != current_user.id:  # type: ignore[arg-type]
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    delete_medical_profile(db, profile_id)


# ---------------------------------------------------------------------------
# Dietary preferences
# ---------------------------------------------------------------------------

@router.get("/dietary", response_model=List[DietaryPreferenceRead])
def list_dietary_preferences(
    skip: int = 0, limit: int = 100,
    current_user: CurrentUser = ...,  # type: ignore[assignment]
    db: DB = ...,  # type: ignore[assignment]
) -> List[DietaryPreferenceRead]:
    return get_dietary_preferences(db, current_user.id, skip=skip, limit=limit)  # type: ignore[return-value]


@router.post("/dietary", response_model=DietaryPreferenceRead, status_code=status.HTTP_201_CREATED)
def create_my_dietary_preference(data_in: DietaryPreferenceCreate, current_user: CurrentUser, db: DB) -> DietaryPreferenceRead:
    return create_dietary_preference(db, current_user.id, data_in)  # type: ignore[return-value]


@router.delete("/dietary/{pref_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_dietary_preference(pref_id: int, current_user: CurrentUser, db: DB) -> None:
    obj = get_dietary_preference(db, pref_id)
    if not obj or int(obj.user_id) != current_user.id:  # type: ignore[arg-type]
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preference not found")
    delete_dietary_preference(db, pref_id)


# ---------------------------------------------------------------------------
# Fitness profiles
# ---------------------------------------------------------------------------

@router.get("/fitness", response_model=List[FitnessProfileRead])
def list_fitness_profiles(
    skip: int = 0, limit: int = 100,
    current_user: CurrentUser = ...,  # type: ignore[assignment]
    db: DB = ...,  # type: ignore[assignment]
) -> List[FitnessProfileRead]:
    return get_fitness_profiles(db, current_user.id, skip=skip, limit=limit)  # type: ignore[return-value]


@router.post("/fitness", response_model=FitnessProfileRead, status_code=status.HTTP_201_CREATED)
def create_my_fitness_profile(data_in: FitnessProfileCreate, current_user: CurrentUser, db: DB) -> FitnessProfileRead:
    return create_fitness_profile(db, current_user.id, data_in)  # type: ignore[return-value]


@router.delete("/fitness/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_fitness_profile(profile_id: int, current_user: CurrentUser, db: DB) -> None:
    obj = get_fitness_profile(db, profile_id)
    if not obj or int(obj.user_id) != current_user.id:  # type: ignore[arg-type]
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    delete_fitness_profile(db, profile_id)


# ---------------------------------------------------------------------------
# Diet recommendations (read-only for users)
# ---------------------------------------------------------------------------

@router.get("/diet-recommendations", response_model=List[DietRecommendationRead])
def list_my_diet_recommendations(
    skip: int = 0, limit: int = 100,
    current_user: CurrentUser = ...,  # type: ignore[assignment]
    db: DB = ...,  # type: ignore[assignment]
) -> List[DietRecommendationRead]:
    return get_diet_recommendations(db, current_user.id, skip=skip, limit=limit)  # type: ignore[return-value]
