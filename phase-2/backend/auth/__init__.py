"""Auth module for JWT verification and user authentication."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from uuid import UUID
from auth.jwt import security, verify_jwt_token


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """FastAPI dependency for extracting current user from JWT token.

    Args:
        credentials: HTTP Authorization header with Bearer token

    Returns:
        Dictionary with user_id (UUID) and email

    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    user_id = verify_jwt_token(token)

    # Note: Phase 2 JWT doesn't store email in token, so we return user_id only
    # The email can be fetched from database if needed
    return {"user_id": user_id, "email": None}


async def validate_user_access(user_id: str, current_user: dict) -> None:
    """Validate that the current user has access to the requested user_id.

    Args:
        user_id: Requested user ID from URL path (string representation of UUID)
        current_user: Current authenticated user from JWT

    Raises:
        HTTPException: If user_id doesn't match authenticated user
    """
    if str(current_user["user_id"]) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own resources",
        )
