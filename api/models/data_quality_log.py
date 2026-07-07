from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String, func

from api.database import Base


class DataQualityLog(Base):
    __tablename__ = "data_quality_logs"

    id = Column(BigInteger, primary_key=True, index=True)
    source_table = Column(String, nullable=False)
    source_record_id = Column(String, nullable=True)
    dag_id = Column(String, nullable=True)
    rule_name = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    message = Column(String, nullable=True)
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    resolved = Column(Boolean, default=False, nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    def __repr__(self) -> str:
        return f"<DataQualityLog id={self.id} rule={self.rule_name!r} resolved={self.resolved}>"
