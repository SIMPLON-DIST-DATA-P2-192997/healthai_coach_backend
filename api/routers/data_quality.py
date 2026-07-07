from typing import List

from fastapi import APIRouter, HTTPException, status

from api.core.deps import CurrentAdmin, DB
from api.crud.data_quality_log import (
    create_data_quality_log, get_data_quality_log,
    get_data_quality_logs, resolve_data_quality_log,
)
from api.schemas.data_quality_log import DataQualityLogCreate, DataQualityLogRead, DataQualityLogResolve

router = APIRouter(prefix="/data-quality", tags=["data-quality"])


@router.get("", response_model=List[DataQualityLogRead])
def list_logs(
    skip: int = 0,
    limit: int = 100,
    resolved: bool | None = None,
    db: DB = ...,  # type: ignore[assignment]
    _: CurrentAdmin = ...,  # type: ignore[assignment]
) -> List[DataQualityLogRead]:
    return get_data_quality_logs(db, skip=skip, limit=limit, resolved=resolved)  # type: ignore[return-value]


@router.get("/{log_id}", response_model=DataQualityLogRead)
def read_log(log_id: int, db: DB, _: CurrentAdmin) -> DataQualityLogRead:
    log = get_data_quality_log(db, log_id)
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")
    return log  # type: ignore[return-value]


@router.post("", response_model=DataQualityLogRead, status_code=status.HTTP_201_CREATED)
def create_log(log_in: DataQualityLogCreate, db: DB, _: CurrentAdmin) -> DataQualityLogRead:
    return create_data_quality_log(db, log_in)  # type: ignore[return-value]


@router.patch("/{log_id}/resolve", response_model=DataQualityLogRead)
def resolve_log(
    log_id: int,
    resolve_data: DataQualityLogResolve,
    current_admin: CurrentAdmin,
    db: DB,
) -> DataQualityLogRead:
    log = get_data_quality_log(db, log_id)
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")
    return resolve_data_quality_log(db, log, resolve_data, current_admin.id)  # type: ignore[return-value]
