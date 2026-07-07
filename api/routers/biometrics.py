from typing import List

from fastapi import APIRouter, HTTPException, status

from api.core.deps import CurrentUser, DB
from api.crud.biometric_measurement import (
    create_measurement, delete_measurement,
    get_measurement, get_measurements_by_user, update_measurement,
)
from api.schemas.biometric_measurement import (
    BiometricMeasurementCreate, BiometricMeasurementRead, BiometricMeasurementUpdate,
)

router = APIRouter(prefix="/biometrics", tags=["biometrics"])


@router.get("", response_model=List[BiometricMeasurementRead])
def list_my_measurements(
    skip: int = 0, limit: int = 100,
    current_user: CurrentUser = ...,  # type: ignore[assignment]
    db: DB = ...,  # type: ignore[assignment]
) -> List[BiometricMeasurementRead]:
    return get_measurements_by_user(db, current_user.id, skip=skip, limit=limit)  # type: ignore[return-value]


@router.post("", response_model=BiometricMeasurementRead, status_code=status.HTTP_201_CREATED)
def create_my_measurement(
    measurement_in: BiometricMeasurementCreate, current_user: CurrentUser, db: DB
) -> BiometricMeasurementRead:
    return create_measurement(db, current_user.id, measurement_in)  # type: ignore[return-value]


@router.get("/{measurement_id}", response_model=BiometricMeasurementRead)
def read_my_measurement(measurement_id: int, current_user: CurrentUser, db: DB) -> BiometricMeasurementRead:
    m = get_measurement(db, measurement_id)
    if not m or int(m.user_id) != current_user.id:  # type: ignore[arg-type]
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Measurement not found")
    return m  # type: ignore[return-value]


@router.put("/{measurement_id}", response_model=BiometricMeasurementRead)
def update_my_measurement(
    measurement_id: int, update_data: BiometricMeasurementUpdate, current_user: CurrentUser, db: DB
) -> BiometricMeasurementRead:
    m = get_measurement(db, measurement_id)
    if not m or int(m.user_id) != current_user.id:  # type: ignore[arg-type]
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Measurement not found")
    return update_measurement(db, m, update_data)  # type: ignore[return-value]


@router.delete("/{measurement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_measurement(measurement_id: int, current_user: CurrentUser, db: DB) -> None:
    m = get_measurement(db, measurement_id)
    if not m or int(m.user_id) != current_user.id:  # type: ignore[arg-type]
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Measurement not found")
    delete_measurement(db, measurement_id)
