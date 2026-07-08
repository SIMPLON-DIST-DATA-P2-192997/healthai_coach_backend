from typing import List

from sqlalchemy.orm import Session

from api.security.security import hash_password
from api.crud.subscription import create_free_subscription
from api.models.user import User
from api.schemas.user import UserAdminUpdate, UserCreate, UserUpdate


def get_user(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()


def create_user(
    db: Session, user_in: UserCreate, is_admin: bool = False
) -> User:
    user = User(
        email=user_in.email,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        date_of_birth=user_in.date_of_birth,
        sex=user_in.sex,
        hashed_password=hash_password(user_in.password),
        is_admin=is_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    create_free_subscription(db, user.id)  # type: ignore[arg-type]
    return user


def update_user(db: Session, user: User, update_data: UserUpdate | UserAdminUpdate) -> User:
    fields = update_data.model_dump(exclude_unset=True)
    for field, value in fields.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    user = get_user(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True
