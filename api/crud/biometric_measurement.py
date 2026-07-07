from typing import List

from sqlalchemy.orm import Session

from api.models.biometric_measurement import BiometricMeasurement
from api.schemas.biometric_measurement import BiometricMeasurementCreate, BiometricMeasurementUpdate


def get_measurement(db: Session, measurement_id: int) -> BiometricMeasurement | None:
    return db.query(BiometricMeasurement).filter(BiometricMeasurement.id == measurement_id).first()


def get_measurements_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[BiometricMeasurement]:
    return (
        db.query(BiometricMeasurement)
        .filter(BiometricMeasurement.user_id == user_id)
        .order_by(BiometricMeasurement.measured_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_measurement(db: Session, user_id: int, measurement_in: BiometricMeasurementCreate) -> BiometricMeasurement:
    measurement = BiometricMeasurement(user_id=user_id, **measurement_in.model_dump())
    db.add(measurement)
    db.commit()
    db.refresh(measurement)
    return measurement


def update_measurement(db: Session, measurement: BiometricMeasurement, update_data: BiometricMeasurementUpdate) -> BiometricMeasurement:
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(measurement, field, value)
    db.commit()
    db.refresh(measurement)
    return measurement


def delete_measurement(db: Session, measurement_id: int) -> bool:
    measurement = get_measurement(db, measurement_id)
    if not measurement:
        return False
    db.delete(measurement)
    db.commit()
    return True
