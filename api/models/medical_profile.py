from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)

from api.database import Base


class MedicalProfile(Base):
    __tablename__ = "medical_profiles"
    __table_args__ = (
        CheckConstraint(
            "severity IN ('Mild', 'Moderate', 'Severe')", name="ck_medical_profiles_severity"
        ),
        CheckConstraint("cholesterol_mg_dl >= 0", name="ck_medical_profiles_cholesterol_mg_dl"),
        CheckConstraint(
            "blood_pressure_mmhg >= 0", name="ck_medical_profiles_blood_pressure_mmhg"
        ),
        CheckConstraint("glucose_mg_dl >= 0", name="ck_medical_profiles_glucose_mg_dl"),
    )

    id = Column(
        "medical_profile_id", BigInteger().with_variant(Integer, "sqlite"), primary_key=True, index=True
    )
    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    disease_type = Column(String(100), nullable=True)
    severity = Column(String(20), nullable=True)
    cholesterol_mg_dl = Column(Numeric(6, 2), nullable=True)
    blood_pressure_mmhg = Column(Numeric(5, 2), nullable=True)
    glucose_mg_dl = Column(Numeric(6, 2), nullable=True)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<MedicalProfile id={self.id} user_id={self.user_id}>"
