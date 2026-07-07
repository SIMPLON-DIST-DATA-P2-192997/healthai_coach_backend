from sqlalchemy import BigInteger, Column, DateTime, String, func

from api.database import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(BigInteger, primary_key=True, index=True)
    external_id = Column(String, nullable=True, index=True)
    source = Column(String, nullable=True)
    name = Column(String, nullable=False)
    body_part = Column(String, nullable=True)
    target_muscle = Column(String, nullable=True)
    equipment = Column(String, nullable=True)
    gif_url = Column(String, nullable=True)
    instructions = Column(String, nullable=True)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<Exercise id={self.id} name={self.name!r}>"
