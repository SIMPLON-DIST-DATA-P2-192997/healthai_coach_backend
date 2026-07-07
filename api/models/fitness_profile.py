from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Numeric, SmallInteger, String

from api.database import Base


class FitnessProfile(Base):
    __tablename__ = "fitness_profiles"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    physical_activity_level = Column(String, nullable=True)
    workout_frequency_days_per_week = Column(SmallInteger, nullable=True)
    experience_level = Column(String, nullable=True)
    weekly_exercise_hours = Column(Numeric(5, 2), nullable=True)
    recorded_at = Column(DateTime(timezone=True), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<FitnessProfile id={self.id} user_id={self.user_id}>"
