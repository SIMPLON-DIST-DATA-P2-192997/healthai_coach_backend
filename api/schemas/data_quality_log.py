from datetime import datetime
from typing import Literal

from pydantic import BaseModel

Severity = Literal["info", "warning", "error", "critical"]


class DataQualityLogBase(BaseModel):
    source_table: str
    source_record_id: str | None = None
    dag_id: str | None = None
    rule_name: str
    severity: Severity
    message: str


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
