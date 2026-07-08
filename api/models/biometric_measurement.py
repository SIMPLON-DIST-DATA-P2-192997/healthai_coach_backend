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
    UniqueConstraint,
    func,
    text,
)

from api.database import Base


class BiometricMeasurement(Base):
    __tablename__ = "biometric_measurements"
    __table_args__ = (
        UniqueConstraint("user_id", "measured_at", name="uq_biometric_user_measured_at"),
        CheckConstraint("weight_kg > 0", name="ck_biometric_measurements_weight_kg"),
        CheckConstraint("height_cm > 0", name="ck_biometric_measurements_height_cm"),
        CheckConstraint(
            "body_fat_pct BETWEEN 0 AND 100", name="ck_biometric_measurements_body_fat_pct"
        ),
        CheckConstraint("muscle_mass_kg >= 0", name="ck_biometric_measurements_muscle_mass_kg"),
        CheckConstraint(
            "resting_heart_rate > 0", name="ck_biometric_measurements_resting_heart_rate"
        ),
    )

    id = Column(
        "measurement_id", BigInteger().with_variant(Integer, "sqlite"), primary_key=True, index=True
    )
    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    measured_at = Column(DateTime(timezone=True), nullable=False, index=True)
    weight_kg = Column(Numeric(5, 2), nullable=True)
    height_cm = Column(Numeric(5, 2), nullable=True)
    body_fat_pct = Column(Numeric(4, 2), nullable=True)
    muscle_mass_kg = Column(Numeric(5, 2), nullable=True)
    resting_heart_rate = Column(SmallInteger, nullable=True)
    source = Column(String(50), nullable=False, server_default=text("'manual'"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<BiometricMeasurement id={self.id} user_id={self.user_id}>"
