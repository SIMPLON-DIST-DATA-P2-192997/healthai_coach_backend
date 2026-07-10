from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    UniqueConstraint,
)

from api.database import Base


class WorkoutSet(Base):
    __tablename__ = "workout_sets"
    __table_args__ = (
        UniqueConstraint(
            "session_id", "exercise_id", "set_number", name="uq_workout_sets_session_exercise_set"
        ),
        CheckConstraint("set_number > 0", name="ck_workout_sets_set_number"),
        CheckConstraint("reps >= 0", name="ck_workout_sets_reps"),
        CheckConstraint("weight_kg >= 0", name="ck_workout_sets_weight_kg"),
        CheckConstraint("duration_seconds >= 0", name="ck_workout_sets_duration_seconds"),
        CheckConstraint("distance_m >= 0", name="ck_workout_sets_distance_m"),
    )

    id = Column("set_id", BigInteger().with_variant(Integer, "sqlite"), primary_key=True, index=True)
    session_id = Column(
        BigInteger,
        ForeignKey("workout_sessions.session_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    exercise_id = Column(
        Integer, ForeignKey("exercises.exercise_id", ondelete="RESTRICT"), nullable=False
    )
    set_number = Column(SmallInteger, nullable=False)
    reps = Column(SmallInteger, nullable=True)
    weight_kg = Column(Numeric(6, 2), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    distance_m = Column(Numeric(8, 2), nullable=True)

    def __repr__(self) -> str:
        return f"<WorkoutSet id={self.id} session_id={self.session_id}>"
