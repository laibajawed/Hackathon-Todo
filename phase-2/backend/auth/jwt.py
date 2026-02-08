"""
JWT token verification and validation.
Provides middleware for validating JWT tokens from Better Auth.
"""
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
from uuid import UUID
from config import settings


security = HTTPBearer()


def create_jwt_token(user_id: UUID) -> str:
    """
    Create a JWT token for a user.

    Args:
        user_id: User's UUID

    Returns:
        Encoded JWT token as string
    """
    expiration = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    payload = {
        "sub": str(user_id),  # Subject (user ID)
        "exp": expiration,  # Expiration time
        "iat": datetime.utcnow(),  # Issued at
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


def verify_jwt_token(token: str) -> UUID:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token string

    Returns:
        User ID (UUID) extracted from token

    Raises:
        HTTPException: If token is invalid, expired, or missing user ID
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )
        return UUID(user_id_str)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: malformed user ID"
        )
