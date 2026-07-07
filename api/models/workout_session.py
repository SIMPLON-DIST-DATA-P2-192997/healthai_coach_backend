from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, SmallInteger, String, func

from api.database import Base


class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=False, index=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    max_bpm = Column(SmallInteger, nullable=True)
    avg_bpm = Column(SmallInteger, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<WorkoutSession id={self.id} user_id={self.user_id}>"
