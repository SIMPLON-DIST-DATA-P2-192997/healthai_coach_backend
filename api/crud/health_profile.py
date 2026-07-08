from typing import List

from sqlalchemy.orm import Session

from api.models.medical_profile import MedicalProfile
from api.models.dietary_preference import DietaryPreference
from api.models.fitness_profile import FitnessProfile
from api.models.diet_recommendation import DietRecommendation
from api.schemas.medical_profile import MedicalProfileCreate
from api.schemas.dietary_preference import DietaryPreferenceCreate
from api.schemas.fitness_profile import FitnessProfileCreate
from api.schemas.diet_recommendation import DietRecommendationCreate


# ---------------------------------------------------------------------------
# Medical Profiles
# ---------------------------------------------------------------------------

def get_medical_profiles(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[MedicalProfile]:
    return (
        db.query(MedicalProfile)
        .filter(MedicalProfile.user_id == user_id)
        .order_by(MedicalProfile.recorded_at.desc())
        .offset(skip).limit(limit).all()
    )


def create_medical_profile(db: Session, user_id: int, data_in: MedicalProfileCreate) -> MedicalProfile:
    obj = MedicalProfile(user_id=user_id, **data_in.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_medical_profile(db: Session, profile_id: int) -> MedicalProfile | None:
    return db.query(MedicalProfile).filter(MedicalProfile.id == profile_id).first()


def delete_medical_profile(db: Session, profile_id: int) -> bool:
    obj = get_medical_profile(db, profile_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


# ---------------------------------------------------------------------------
# Dietary Preferences
# ---------------------------------------------------------------------------

def get_dietary_preferences(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[DietaryPreference]:
    return (
        db.query(DietaryPreference)
        .filter(DietaryPreference.user_id == user_id)
        .order_by(DietaryPreference.recorded_at.desc())
        .offset(skip).limit(limit).all()
    )


def create_dietary_preference(db: Session, user_id: int, data_in: DietaryPreferenceCreate) -> DietaryPreference:
    obj = DietaryPreference(user_id=user_id, **data_in.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_dietary_preference(db: Session, pref_id: int) -> DietaryPreference | None:
    return db.query(DietaryPreference).filter(DietaryPreference.id == pref_id).first()


def delete_dietary_preference(db: Session, pref_id: int) -> bool:
    obj = get_dietary_preference(db, pref_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


# ---------------------------------------------------------------------------
# Fitness Profiles
# ---------------------------------------------------------------------------

def get_fitness_profiles(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[FitnessProfile]:
    return (
        db.query(FitnessProfile)
        .filter(FitnessProfile.user_id == user_id)
        .order_by(FitnessProfile.recorded_at.desc())
        .offset(skip).limit(limit).all()
    )


def create_fitness_profile(db: Session, user_id: int, data_in: FitnessProfileCreate) -> FitnessProfile:
    obj = FitnessProfile(user_id=user_id, **data_in.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_fitness_profile(db: Session, profile_id: int) -> FitnessProfile | None:
    return db.query(FitnessProfile).filter(FitnessProfile.id == profile_id).first()


def delete_fitness_profile(db: Session, profile_id: int) -> bool:
    obj = get_fitness_profile(db, profile_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


# ---------------------------------------------------------------------------
# Diet Recommendations
# ---------------------------------------------------------------------------

def get_diet_recommendations(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[DietRecommendation]:
    return (
        db.query(DietRecommendation)
        .filter(DietRecommendation.user_id == user_id)
        .order_by(DietRecommendation.recommended_at.desc())
        .offset(skip).limit(limit).all()
    )


def create_diet_recommendation(db: Session, user_id: int, data_in: DietRecommendationCreate) -> DietRecommendation:
    obj = DietRecommendation(user_id=user_id, **data_in.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_diet_recommendation(db: Session, rec_id: int) -> DietRecommendation | None:
    return db.query(DietRecommendation).filter(DietRecommendation.id == rec_id).first()
