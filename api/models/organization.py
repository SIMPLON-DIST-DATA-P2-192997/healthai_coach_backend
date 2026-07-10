from sqlalchemy import Column, DateTime, Integer, String, func

from api.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column("organization_id", Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    contact_email = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<Organization id={self.id} name={self.name!r}>"
