from __future__ import annotations

from datetime import datetime, timedelta

from pydantic import EmailStr
from sqlalchemy import delete, func
from sqlmodel import Session, select

from app.core.config import settings
from app.core.security import (
    generate_session_token,
    hash_password,
    hash_session_token,
    verify_password,
)
from app.models.entities import AuthSession, User
from app.schemas.auth import AuthUser, RegistrationRequest, UpdateProfileRequest


def get_user_by_email(session: Session, email: EmailStr) -> User | None:
    statement = select(User).where(func.lower(User.email) == email.lower())
    return session.exec(statement).first()


def create_user(session: Session, payload: RegistrationRequest) -> User:
    display_name = payload.display_name or payload.email.split("@", 1)[0]
    user = User(
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        display_name=display_name,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def verify_user_credentials(session: Session, email: EmailStr, password: str) -> User | None:
    user = get_user_by_email(session, email)
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def create_session(session: Session, user: User) -> str:
    raw_token = generate_session_token()
    auth_session = AuthSession(
        user_id=user.id,
        token_hash=hash_session_token(raw_token),
        expires_at=datetime.utcnow() + timedelta(hours=settings.session_ttl_hours),
    )
    session.add(auth_session)
    session.commit()
    return raw_token


def get_user_by_session_token(session: Session, raw_token: str) -> User | None:
    token_hash = hash_session_token(raw_token)
    auth_session = session.exec(
        select(AuthSession).where(
            AuthSession.token_hash == token_hash,
            AuthSession.expires_at > datetime.utcnow(),
        )
    ).first()
    if auth_session is None:
        return None
    return session.get(User, auth_session.user_id)


def destroy_session(session: Session, user_id: str) -> None:
    session.exec(delete(AuthSession).where(AuthSession.user_id == user_id))
    session.commit()


def update_user_profile(session: Session, user: User, payload: UpdateProfileRequest) -> User:
    normalized_display_name = (payload.display_name or "").strip() or user.email.split("@", 1)[0]
    user.display_name = normalized_display_name
    user.updated_at = datetime.utcnow()
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def serialize_user(user: User) -> AuthUser:
    return AuthUser(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        created_at=user.created_at,
    )
