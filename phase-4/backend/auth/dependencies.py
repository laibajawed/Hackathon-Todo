"""
FastAPI dependencies for authentication.
Provides dependency functions to extract and validate current user from JWT.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from uuid import UUID
from auth.jwt import security, verify_jwt_token


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UUID:
    """
    FastAPI dependency to get current authenticated user ID from JWT token.

    Extracts JWT token from Authorization header, validates it, and returns user ID.
    This dependency should be used on all protected endpoints.

    Args:
        credentials: HTTP Bearer credentials from Authorization header

    Returns:
        User ID (UUID) of authenticated user

    Raises:
        HTTPException: If token is missing, invalid, or expired
    """
    token = credentials.credentials
    user_id = verify_jwt_token(token)
    return user_id
