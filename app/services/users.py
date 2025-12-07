from typing import Optional
from sqlalchemy.orm import Session

from app.db.models import User
from app.core.security import hash_password, verify_password


class IdentifierAlreadyUsedError(Exception):
    pass


def get_user_by_identifier(db: Session, identifier: str) -> Optional[User]:
    return db.query(User).filter(User.identifier == identifier).first()


def create_user(db: Session, identifier: str, password: str) -> User:
    existing = get_user_by_identifier(db, identifier)
    if existing:
        raise IdentifierAlreadyUsedError("Identifier already in use")

    user = User(
        identifier=identifier,
        password_hash=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, identifier: str, password: str) -> Optional[User]:
    user = get_user_by_identifier(db, identifier)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
