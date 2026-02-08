"""
Authentication routes for user signup and signin.
Provides endpoints for user registration and authentication.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_session
from models import User
from auth.schemas import UserSignup, UserSignin, AuthResponse, UserResponse
from auth.utils import hash_password, verify_password
from auth.jwt import create_jwt_token
import html


router = APIRouter()


def sanitize_input(text: str) -> str:
    """Escape HTML entities to prevent XSS attacks."""
    return html.escape(text)


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserSignup,
    session: AsyncSession = Depends(get_session)
):
    """
    Register a new user account.

    Creates a new user with hashed password and returns JWT token.

    Args:
        user_data: User signup data (email and password)
        session: Database session

    Returns:
        AuthResponse with user data and JWT token

    Raises:
        HTTPException: If email already exists (409 Conflict)
    """
    # Normalize email to lowercase
    email = user_data.email.lower()

    # Check if user already exists
    statement = select(User).where(User.email == email)
    result = await session.execute(statement)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Hash password
    password_hash = hash_password(user_data.password)

    # Create new user
    new_user = User(
        email=email,
        password_hash=password_hash
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    # Generate JWT token
    token = create_jwt_token(new_user.id)

    # Return user data and token
    user_response = UserResponse(
        id=new_user.id,
        email=new_user.email,
        created_at=new_user.created_at
    )

    return AuthResponse(user=user_response, token=token)


@router.post("/signin", response_model=AuthResponse)
async def signin(
    user_data: UserSignin,
    session: AsyncSession = Depends(get_session)
):
    """
    Authenticate a user and return JWT token.

    Verifies credentials and returns JWT token for authenticated user.

    Args:
        user_data: User signin data (email and password)
        session: Database session

    Returns:
        AuthResponse with user data and JWT token

    Raises:
        HTTPException: If credentials are invalid (401 Unauthorized)
    """
    # Normalize email to lowercase
    email = user_data.email.lower()

    # Find user by email
    statement = select(User).where(User.email == email)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Generate JWT token
    token = create_jwt_token(user.id)

    # Return user data and token
    user_response = UserResponse(
        id=user.id,
        email=user.email,
        created_at=user.created_at
    )

    return AuthResponse(user=user_response, token=token)
