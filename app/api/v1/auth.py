# app/api/v1/auth.py

from fastapi import (
    APIRouter,
    Depends,
    status,
    UploadFile,
    File,
)
import os
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.jsend import jsend_success, jsend_fail
from app.core.security import create_access_token
from app.core.deps import get_current_user
from app.db.base import get_db
from app.db.models import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.schemas.user import UserBase
from app.schemas.responses import AuthResponse, AvatarResponse, MessageResponse
from app.services import users as user_service
from app.services.users import IdentifierAlreadyUsedError
from app.core.ws_manager import manager

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    summary="Register new user",
    description="Create account with identifier (nickname, email, or phone) and password. "
                "No confirmation required. Returns user info and JWT access token.",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    try:
        user = user_service.create_user(
            db, identifier=payload.identifier, password=payload.password
        )
    except IdentifierAlreadyUsedError as e:
        return jsend_fail(
            {"identifier": str(e)},
            http_status=status.HTTP_400_BAD_REQUEST,
        )

    access_token = create_access_token(subject=str(user.id))

    data = {
        "user": UserBase.model_validate(user).model_dump(),
        "token": TokenResponse(access_token=access_token).model_dump(),
    }
    return jsend_success(data, http_status=status.HTTP_201_CREATED)


@router.post(
    "/login",
    summary="Login",
    description="Authenticate with identifier and password. "
                "Returns user info and JWT access token on success.",
    response_model=AuthResponse,
)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = user_service.authenticate_user(
        db, identifier=payload.identifier, password=payload.password
    )
    if not user:
        return jsend_fail(
            {"credentials": "Invalid identifier or password"},
            http_status=status.HTTP_401_UNAUTHORIZED,
        )

    access_token = create_access_token(subject=str(user.id))
    data = {
        "user": UserBase.model_validate(user).model_dump(),
        "token": TokenResponse(access_token=access_token).model_dump(),
    }
    return jsend_success(data)


@router.get(
    "/ping",
    summary="Ping auth service",
    description="Simple connectivity test for auth endpoints.",
    response_model=MessageResponse,
)
def ping():
    return jsend_success({"message": "auth works"})


AVATAR_DIR = "static/avatars"


@router.post(
    "/avatar",
    summary="Upload avatar",
    description="Upload or replace current user's avatar image (PNG/JPEG). "
                "Returns the uploaded image URL. Connected WebSocket clients "
                "will receive an avatar_changed event.",
    response_model=AvatarResponse,
)
async def upload_avatar(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # --- delete OLD avatar file if exists ---
    if user.avatar_url:
        old_filename = os.path.basename(user.avatar_url)
        old_path = os.path.join(AVATAR_DIR, old_filename)
        try:
            if os.path.exists(old_path):
                os.remove(old_path)
        except OSError:
            # don't break upload if cleanup fails
            pass

    # --- file validation ---
    if file.content_type not in ("image/png", "image/jpeg", "image/jpg"):
        return jsend_fail(
            {"file": "Only PNG and JPEG images are allowed"},
            http_status=status.HTTP_400_BAD_REQUEST,
        )

    os.makedirs(AVATAR_DIR, exist_ok=True)

    _, ext = os.path.splitext(file.filename or "")
    if ext.lower() not in (".png", ".jpg", ".jpeg"):
        ext = ".png" if file.content_type == "image/png" else ".jpg"

    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    filename = f"user_{user.id}_{timestamp}{ext}"
    file_path = os.path.join(AVATAR_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    avatar_url = f"/static/avatars/{filename}"

    user.avatar_url = avatar_url
    db.add(user)
    db.commit()
    db.refresh(user)

    await manager.broadcast_avatar_changed(user_id=user.id, avatar_url=avatar_url)

    return jsend_success({"avatar_url": avatar_url}, http_status=status.HTTP_200_OK)


@router.delete(
    "/me",
    summary="Delete current user",
    description="Permanently delete user account, remove avatar file from disk, "
                "and close all active WebSocket connections. "
                "Previously issued tokens will no longer work.",
    response_model=MessageResponse,
)
async def delete_current_user_endpoint(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = user.id

    # ---- delete avatar file from disk ----
    if user.avatar_url:
        filename = os.path.basename(user.avatar_url)
        avatar_path = os.path.join(AVATAR_DIR, filename)

        try:
            if os.path.exists(avatar_path):
                os.remove(avatar_path)
        except OSError:
            # Don't crash delete if file is already gone
            pass

    # ---- delete user from DB ----
    db.delete(user)
    db.commit()

    # ---- close all WebSocket connections ----
    await manager.disconnect_user(user_id)

    return jsend_success(
        {"message": "User and avatar deleted"},
        http_status=status.HTTP_200_OK,
    )
