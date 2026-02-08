"""
Pydantic schemas for authentication requests and responses.
Provides validation for user signup, signin, and auth responses.
"""
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime


class UserSignup(BaseModel):
    """Schema for user registration request."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)


class UserSignin(BaseModel):
    """Schema for user signin request."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user data in responses (excludes password)."""
    id: UUID
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Schema for authentication response with user data and JWT token."""
    user: UserResponse
    token: str
