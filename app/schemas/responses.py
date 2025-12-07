# app/schemas/responses.py
"""
JSend-compliant response models for API documentation.
"""

from pydantic import BaseModel
from typing import Optional


# ---- Nested data models ----

class UserData(BaseModel):
    """User information returned in responses."""
    id: int
    identifier: str
    avatar_url: Optional[str] = None


class TokenData(BaseModel):
    """JWT token information."""
    access_token: str
    token_type: str = "bearer"


class AuthData(BaseModel):
    """Combined user + token data for auth responses."""
    user: UserData
    token: TokenData


class AvatarData(BaseModel):
    """Avatar upload response data."""
    avatar_url: str


class MessageData(BaseModel):
    """Simple message response data."""
    message: str


# ---- JSend response wrappers ----

class AuthResponse(BaseModel):
    """JSend success response for register/login endpoints."""
    status: str = "success"
    data: AuthData


class AvatarResponse(BaseModel):
    """JSend success response for avatar upload."""
    status: str = "success"
    data: AvatarData


class MessageResponse(BaseModel):
    """JSend success response with a simple message (delete, health, ping)."""
    status: str = "success"
    data: MessageData


