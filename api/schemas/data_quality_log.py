from datetime import datetime

from pydantic import BaseModel


class DataQualityLogBase(BaseModel):
    source_table: str
    source_record_id: str | None = None
    dag_id: str | None = None
    rule_name: str
    severity: str
    message: str | None = None


class DataQualityLogCreate(DataQualityLogBase):
    pass


class DataQualityLogResolve(BaseModel):
    resolved: bool = True
    resolved_at: datetime | None = None


class DataQualityLogRead(DataQualityLogBase):
    id: int
    detected_at: datetime
    resolved: bool
    resolved_at: datetime | None = None
    resolved_by: int | None = None

    model_config = {"from_attributes": True}
