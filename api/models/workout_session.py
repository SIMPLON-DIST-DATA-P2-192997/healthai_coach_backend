from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    SmallInteger,
    Text,
    func,
)

from api.database import Base


class WorkoutSession(Base):
    __tablename__ = "workout_sessions"
    __table_args__ = (
        CheckConstraint("max_bpm > 0", name="ck_workout_sessions_max_bpm"),
        CheckConstraint("avg_bpm > 0", name="ck_workout_sessions_avg_bpm"),
        CheckConstraint(
            "ended_at IS NULL OR ended_at >= started_at",
            name="ck_workout_sessions_ended_after_started",
        ),
    )

    id = Column("session_id", BigInteger().with_variant(Integer, "sqlite"), primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    started_at = Column(DateTime(timezone=True), nullable=False, index=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    max_bpm = Column(SmallInteger, nullable=True)
    avg_bpm = Column(SmallInteger, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<WorkoutSession id={self.id} user_id={self.user_id}>"
