from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_session
from app.models.entities import User
from app.schemas.auth import AuthUser, LoginRequest, RegistrationRequest
from app.services.auth_service import (
    create_session,
    create_user,
    destroy_session,
    get_user_by_email,
    serialize_user,
    verify_user_credentials,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=int(timedelta(hours=settings.session_ttl_hours).total_seconds()),
        path="/",
    )


@router.post("/register", response_model=AuthUser, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegistrationRequest,
    response: Response,
    session: Session = Depends(get_session),
) -> AuthUser:
    existing = get_user_by_email(session, payload.email)
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already registered.")

    user = create_user(session, payload)
    token = create_session(session, user)
    _set_session_cookie(response, token)
    return serialize_user(user)


@router.post("/login", response_model=AuthUser)
def login(
    payload: LoginRequest,
    response: Response,
    session: Session = Depends(get_session),
) -> AuthUser:
    user = verify_user_credentials(session, payload.email, payload.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    token = create_session(session, user)
    _set_session_cookie(response, token)
    return serialize_user(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Response:
    destroy_session(session, current_user.id)
    response.delete_cookie(key=settings.session_cookie_name, path="/")
    return response


@router.get("/me", response_model=AuthUser)
def me(current_user: User = Depends(get_current_user)) -> AuthUser:
    return serialize_user(current_user)
