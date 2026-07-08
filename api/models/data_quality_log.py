from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)

from api.database import Base


class DataQualityLog(Base):
    __tablename__ = "data_quality_log"
    __table_args__ = (
        CheckConstraint(
            "severity IN ('info', 'warning', 'error', 'critical')",
            name="ck_data_quality_log_severity",
        ),
        CheckConstraint(
            "resolved = TRUE OR (resolved_at IS NULL AND resolved_by IS NULL)",
            name="chk_data_quality_log_resolution_consistency",
        ),
    )

    id = Column("dq_log_id", BigInteger().with_variant(Integer, "sqlite"), primary_key=True, index=True)
    source_table = Column(String(100), nullable=False)
    source_record_id = Column(String(100), nullable=True)
    dag_id = Column(String(150), nullable=True)
    rule_name = Column(String(150), nullable=False)
    severity = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    resolved = Column(Boolean, default=False, nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(
        Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True
    )

    def __repr__(self) -> str:
        return f"<DataQualityLog id={self.id} rule={self.rule_name!r} resolved={self.resolved}>"
