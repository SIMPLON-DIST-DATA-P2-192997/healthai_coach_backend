from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Numeric, String

from api.database import Base


class MedicalProfile(Base):
    __tablename__ = "medical_profiles"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    disease_type = Column(String, nullable=True)
    severity = Column(String, nullable=True)
    cholesterol_mg_dl = Column(Numeric(7, 2), nullable=True)
    blood_pressure_mmhg = Column(Numeric(7, 2), nullable=True)
    glucose_mg_dl = Column(Numeric(7, 2), nullable=True)
    recorded_at = Column(DateTime(timezone=True), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<MedicalProfile id={self.id} user_id={self.user_id}>"
