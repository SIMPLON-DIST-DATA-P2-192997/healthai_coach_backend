from sqlalchemy import BigInteger, Column, ForeignKey, Integer, Numeric, SmallInteger

from api.database import Base


class WorkoutSet(Base):
    __tablename__ = "workout_sets"

    id = Column(BigInteger, primary_key=True, index=True)
    session_id = Column(BigInteger, ForeignKey("workout_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    exercise_id = Column(BigInteger, ForeignKey("exercises.id", ondelete="RESTRICT"), nullable=False)
    set_number = Column(SmallInteger, nullable=True)
    reps = Column(SmallInteger, nullable=True)
    weight_kg = Column(Numeric(6, 2), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    distance_m = Column(Numeric(8, 2), nullable=True)

    def __repr__(self) -> str:
        return f"<WorkoutSet id={self.id} session_id={self.session_id}>"
