from datetime import datetime, timezone
from typing import List

from sqlalchemy.orm import Session

from api.models.data_quality_log import DataQualityLog
from api.schemas.data_quality_log import DataQualityLogCreate, DataQualityLogResolve


def get_data_quality_log(db: Session, log_id: int) -> DataQualityLog | None:
    return db.query(DataQualityLog).filter(DataQualityLog.id == log_id).first()


def get_data_quality_logs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    resolved: bool | None = None,
) -> List[DataQualityLog]:
    q = db.query(DataQualityLog)
    if resolved is not None:
        q = q.filter(DataQualityLog.resolved == resolved)
    return q.order_by(DataQualityLog.detected_at.desc()).offset(skip).limit(limit).all()


def create_data_quality_log(db: Session, log_in: DataQualityLogCreate) -> DataQualityLog:
    log = DataQualityLog(**log_in.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def resolve_data_quality_log(
    db: Session,
    log: DataQualityLog,
    resolve_data: DataQualityLogResolve,
    resolved_by_id: int,
) -> DataQualityLog:
    log.resolved = resolve_data.resolved
    log.resolved_at = resolve_data.resolved_at or datetime.now(timezone.utc)
    log.resolved_by = resolved_by_id
    db.commit()
    db.refresh(log)
    return log
