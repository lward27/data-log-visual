from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status
from sqlmodel import Session

from app.core.config import settings
from app.db.session import get_session
from app.models.entities import User
from app.services.auth_service import get_user_by_session_token


def get_current_user(
    request: Request,
    session: Session = Depends(get_session),
) -> User:
    session_token = request.cookies.get(settings.session_cookie_name)
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    user = get_user_by_session_token(session, session_token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session is invalid or expired.",
        )

    return user
