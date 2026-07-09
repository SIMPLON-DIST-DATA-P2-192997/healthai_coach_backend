from typing import Annotated, Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from api.security.security import decode_token
from api.crud.subscription import get_active_subscription
from api.database import SessionLocal
from api.models.user import User
from api.schemas.token import TokenData

PREMIUM_TIERS = {"premium", "premium_plus", "b2b"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Authentication dependencies
# ---------------------------------------------------------------------------

def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        sub: str | None = payload.get("sub")
        if sub is None:
            raise credentials_exc
        TokenData(sub=sub, is_admin=payload.get("is_admin"))  # validate shape
    except JWTError:
        raise credentials_exc

    user: User | None = db.query(User).filter(User.id == int(sub)).first()
    if user is None:
        raise credentials_exc
    return user


def get_current_admin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not bool(current_user.is_admin):  # type: ignore[arg-type]
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


def get_current_premium_user(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Gate premium-only features (AI-generated content) behind an active
    premium/premium_plus/b2b subscription. Everyone starts on `free`
    (cf. api/crud/user.create_user), so a missing subscription is treated
    the same as `free`."""
    subscription = get_active_subscription(db, current_user.id)  # type: ignore[arg-type]
    tier = subscription.tier if subscription else "free"
    if tier not in PREMIUM_TIERS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This feature requires a premium subscription",
        )
    return current_user


# ---------------------------------------------------------------------------
# Type aliases for cleaner router signatures
# ---------------------------------------------------------------------------

CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentAdmin = Annotated[User, Depends(get_current_admin)]
CurrentPremiumUser = Annotated[User, Depends(get_current_premium_user)]
DB = Annotated[Session, Depends(get_db)]
