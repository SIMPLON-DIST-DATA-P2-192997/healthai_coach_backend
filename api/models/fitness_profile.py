from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    func,
)

from api.database import Base


class FitnessProfile(Base):
    __tablename__ = "fitness_profiles"
    __table_args__ = (
        CheckConstraint(
            "workout_frequency_days_per_week BETWEEN 0 AND 7",
            name="ck_fitness_profiles_workout_frequency_days_per_week",
        ),
        CheckConstraint(
            "weekly_exercise_hours >= 0", name="ck_fitness_profiles_weekly_exercise_hours"
        ),
    )

    id = Column(
        "fitness_profile_id", BigInteger().with_variant(Integer, "sqlite"), primary_key=True, index=True
    )
    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    physical_activity_level = Column(String(20), nullable=True)
    workout_frequency_days_per_week = Column(SmallInteger, nullable=True)
    experience_level = Column(String(20), nullable=True)
    weekly_exercise_hours = Column(Numeric(5, 2), nullable=True)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<FitnessProfile id={self.id} user_id={self.user_id}>"
