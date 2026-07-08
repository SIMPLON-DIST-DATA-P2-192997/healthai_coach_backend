from sqlalchemy import Column, DateTime, Integer, String, Text, UniqueConstraint, func, text

from api.database import Base


class Exercise(Base):
    __tablename__ = "exercises"
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_exercises_source_external_id"),
    )

    id = Column("exercise_id", Integer, primary_key=True, index=True)
    external_id = Column(String(100), nullable=True, index=True)
    source = Column(String(50), nullable=False, server_default=text("'exercisedb'"))
    name = Column(String(255), nullable=False)
    body_part = Column(String(100), nullable=True)
    target_muscle = Column(String(100), nullable=True)
    equipment = Column(String(100), nullable=True)
    gif_url = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<Exercise id={self.id} name={self.name!r}>"
