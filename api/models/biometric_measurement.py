from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint, func

from api.database import Base


class BiometricMeasurement(Base):
    __tablename__ = "biometric_measurements"
    __table_args__ = (
        UniqueConstraint("user_id", "measured_at", name="uq_biometric_user_measured_at"),
    )

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    measured_at = Column(DateTime(timezone=True), nullable=False, index=True)
    weight_kg = Column(Numeric(5, 2), nullable=True)
    height_cm = Column(Numeric(5, 2), nullable=True)
    body_fat_pct = Column(Numeric(5, 2), nullable=True)
    muscle_mass_kg = Column(Numeric(5, 2), nullable=True)
    resting_heart_rate = Column(Integer, nullable=True)
    source = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<BiometricMeasurement id={self.id} user_id={self.user_id}>"
