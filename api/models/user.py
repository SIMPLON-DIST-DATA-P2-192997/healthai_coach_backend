from sqlalchemy import Boolean, CheckConstraint, Column, Date, DateTime, Integer, String, func

from api.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("sex IN ('F', 'M', 'other')", name="ck_users_sex"),
    )

    id = Column("user_id", Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    sex = Column(String(10), nullable=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} is_admin={self.is_admin}>"
