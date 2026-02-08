# Authentication Flow

**Feature**: Todo Full-Stack Web Application (Basic Level)
**Date**: 2026-01-13
**Status**: Final

## Overview

This document describes the authentication flows for Phase 2, including user registration (signup), user authentication (signin), JWT token lifecycle, and error handling scenarios.

## Authentication Architecture

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Frontend   │         │   Backend    │         │   Database   │
│  (Next.js)   │         │  (FastAPI)   │         │ (PostgreSQL) │
└──────┬───────┘         └──────┬───────┘         └──────┬───────┘
       │                        │                        │
       │  Better Auth           │  PyJWT                 │
       │  (JWT Plugin)          │  (Validation)          │
       │                        │                        │
```

**Key Components**:
- **Frontend**: Better Auth library handles signup/signin UI and token storage
- **Backend**: FastAPI validates JWT tokens and enforces user isolation
- **JWT Secret**: Shared secret between frontend and backend for token signing/validation

---

## 1. User Registration (Signup) Flow

### Flow Diagram

```
┌─────────┐                                                    ┌─────────┐
│  User   │                                                    │ Browser │
└────┬────┘                                                    └────┬────┘
     │                                                              │
     │ 1. Navigate to /auth/signup                                 │
     │────────────────────────────────────────────────────────────>│
     │                                                              │
     │ 2. Enter email & password                                   │
     │────────────────────────────────────────────────────────────>│
     │                                                              │
     │                                                              │
┌────┴────┐                                                    ┌───┴────┐
│Frontend │                                                    │Backend │
└────┬────┘                                                    └───┬────┘
     │                                                              │
     │ 3. POST /api/auth/signup                                    │
     │  { email, password }                                        │
     │─────────────────────────────────────────────────────────────>│
     │                                                              │
     │                                                              │ 4. Validate input
     │                                                              │    (email format,
     │                                                              │     password length)
     │                                                              │
     │                                                              │ 5. Check email uniqueness
     │                                                              │────────┐
     │                                                              │        │ SELECT * FROM user
     │                                                              │<───────┘ WHERE email = ?
     │                                                              │
     │                                                              │ 6. Hash password (bcrypt)
     │                                                              │
     │                                                              │ 7. Create user record
     │                                                              │────────┐
     │                                                              │        │ INSERT INTO user
     │                                                              │<───────┘
     │                                                              │
     │                                                              │ 8. Generate JWT token
     │                                                              │    (sub: user_id,
     │                                                              │     exp: 24h)
     │                                                              │
     │ 9. Return user + token                                      │
     │<─────────────────────────────────────────────────────────────│
     │  { user: {...}, token: "..." }                              │
     │                                                              │
     │ 10. Store token in httpOnly cookie                          │
     │     or localStorage                                         │
     │                                                              │
     │ 11. Redirect to /tasks                                      │
     │────────────────────────────────────────────────────────────>│
     │                                                              │
```

### Request/Response

**Request**:
```http
POST /api/auth/signup HTTP/1.1
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Success Response (201 Created)**:
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "created_at": "2026-01-13T10:00:00Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJleHAiOjE3MDUyMzg0MDB9.signature"
}
```

**Error Responses**:

*Invalid Email Format (400)*:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": { "field": "email" }
  }
}
```

*Email Already Registered (409)*:
```json
{
  "error": {
    "code": "CONFLICT",
    "message": "Email already registered",
    "details": {}
  }
}
```

*Password Too Short (400)*:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Password must be at least 8 characters",
    "details": { "field": "password" }
  }
}
```

### Implementation Notes

1. **Password Hashing**: Use bcrypt with cost factor 12 (FR-017)
2. **Email Normalization**: Convert email to lowercase before storage
3. **Token Generation**: JWT contains `sub` (user_id) and `exp` (expiration) claims
4. **Token Expiration**: 24 hours from issuance
5. **Automatic Login**: User is immediately authenticated after signup

---

## 2. User Authentication (Signin) Flow

### Flow Diagram

```
┌─────────┐                                                    ┌─────────┐
│  User   │                                                    │ Browser │
└────┬────┘                                                    └────┬────┘
     │                                                              │
     │ 1. Navigate to /auth/signin                                 │
     │────────────────────────────────────────────────────────────>│
     │                                                              │
     │ 2. Enter email & password                                   │
     │────────────────────────────────────────────────────────────>│
     │                                                              │
     │                                                              │
┌────┴────┐                                                    ┌───┴────┐
│Frontend │                                                    │Backend │
└────┬────┘                                                    └───┬────┘
     │                                                              │
     │ 3. POST /api/auth/signin                                    │
     │  { email, password }                                        │
     │─────────────────────────────────────────────────────────────>│
     │                                                              │
     │                                                              │ 4. Find user by email
     │                                                              │────────┐
     │                                                              │        │ SELECT * FROM user
     │                                                              │<───────┘ WHERE email = ?
     │                                                              │
     │                                                              │ 5. Verify password
     │                                                              │    (bcrypt.verify)
     │                                                              │
     │                                                              │ 6. Generate JWT token
     │                                                              │    (sub: user_id,
     │                                                              │     exp: 24h)
     │                                                              │
     │ 7. Return user + token                                      │
     │<─────────────────────────────────────────────────────────────│
     │  { user: {...}, token: "..." }                              │
     │                                                              │
     │ 8. Store token in httpOnly cookie                           │
     │     or localStorage                                         │
     │                                                              │
     │ 9. Redirect to /tasks                                       │
     │────────────────────────────────────────────────────────────>│
     │                                                              │
```

### Request/Response

**Request**:
```http
POST /api/auth/signin HTTP/1.1
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Success Response (200 OK)**:
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "created_at": "2026-01-13T10:00:00Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJleHAiOjE3MDUyMzg0MDB9.signature"
}
```

**Error Response (401 Unauthorized)**:
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid email or password",
    "details": {}
  }
}
```

### Implementation Notes

1. **Password Verification**: Use bcrypt.verify() to compare hashed password
2. **Generic Error Message**: Don't reveal whether email exists (security best practice)
3. **Rate Limiting**: Consider implementing rate limiting to prevent brute force attacks (future enhancement)
4. **Token Generation**: Same JWT structure as signup

---

## 3. JWT Token Structure

### Token Format

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJleHAiOjE3MDUyMzg0MDB9.signature
│                                      │                                                                                  │
│         Header (Base64)              │                      Payload (Base64)                                           │  Signature
```

### Decoded Token

**Header**:
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload**:
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",  // User ID
  "exp": 1705238400,                               // Expiration timestamp (24h from issuance)
  "iat": 1705152000                                // Issued at timestamp
}
```

**Signature**:
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  JWT_SECRET
)
```

### Token Lifecycle

```
┌──────────┐
│  Issued  │ (signup or signin)
└────┬─────┘
     │
     │ Valid for 24 hours
     │
     ▼
┌──────────┐
│  Active  │ (used for API requests)
└────┬─────┘
     │
     │ After 24 hours
     │
     ▼
┌──────────┐
│ Expired  │ (user must re-authenticate)
└──────────┘
```

### Token Storage

**Frontend Options**:

1. **httpOnly Cookie** (Recommended):
   - Pros: XSS protection, automatic inclusion in requests
   - Cons: CSRF vulnerability (mitigated with SameSite attribute)

2. **localStorage**:
   - Pros: Simple to implement, works across tabs
   - Cons: Vulnerable to XSS attacks

**Phase 2 Decision**: Use httpOnly cookies for security

---

## 4. Protected API Request Flow

### Flow Diagram

```
┌─────────┐                                                    ┌─────────┐
│  User   │                                                    │ Browser │
└────┬────┘                                                    └────┬────┘
     │                                                              │
     │ 1. Click "View Tasks"                                       │
     │────────────────────────────────────────────────────────────>│
     │                                                              │
     │                                                              │
┌────┴────┐                                                    ┌───┴────┐
│Frontend │                                                    │Backend │
└────┬────┘                                                    └───┬────┘
     │                                                              │
     │ 2. GET /api/tasks                                           │
     │    Authorization: Bearer <token>                            │
     │─────────────────────────────────────────────────────────────>│
     │                                                              │
     │                                                              │ 3. Extract token from
     │                                                              │    Authorization header
     │                                                              │
     │                                                              │ 4. Verify JWT signature
     │                                                              │    (using JWT_SECRET)
     │                                                              │
     │                                                              │ 5. Check expiration
     │                                                              │    (exp claim)
     │                                                              │
     │                                                              │ 6. Extract user_id
     │                                                              │    (sub claim)
     │                                                              │
     │                                                              │ 7. Query tasks
     │                                                              │────────┐
     │                                                              │        │ SELECT * FROM task
     │                                                              │<───────┘ WHERE user_id = ?
     │                                                              │
     │ 8. Return tasks                                             │
     │<─────────────────────────────────────────────────────────────│
     │  [{ id, title, ... }]                                       │
     │                                                              │
```

### Request/Response

**Request**:
```http
GET /api/tasks HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Success Response (200 OK)**:
```json
[
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Complete project documentation",
    "description": "Write comprehensive docs for Phase 2",
    "status": "pending",
    "created_at": "2026-01-13T10:00:00Z",
    "updated_at": "2026-01-13T10:00:00Z"
  }
]
```

**Error Responses**:

*Missing Token (401)*:
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Missing authorization token",
    "details": {}
  }
}
```

*Invalid Token (401)*:
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid token",
    "details": {}
  }
}
```

*Expired Token (401)*:
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Token expired",
    "details": {}
  }
}
```

---

## 5. Token Expiration Handling

### Scenario: Token Expires During Session

```
┌─────────┐                                                    ┌─────────┐
│  User   │                                                    │ Browser │
└────┬────┘                                                    └────┬────┘
     │                                                              │
     │ 1. Perform action (e.g., create task)                       │
     │────────────────────────────────────────────────────────────>│
     │                                                              │
     │                                                              │
┌────┴────┐                                                    ┌───┴────┐
│Frontend │                                                    │Backend │
└────┬────┘                                                    └───┬────┘
     │                                                              │
     │ 2. POST /api/tasks                                          │
     │    Authorization: Bearer <expired_token>                    │
     │─────────────────────────────────────────────────────────────>│
     │                                                              │
     │                                                              │ 3. Verify token
     │                                                              │    → EXPIRED
     │                                                              │
     │ 4. 401 Unauthorized                                         │
     │<─────────────────────────────────────────────────────────────│
     │  { error: "Token expired" }                                 │
     │                                                              │
     │ 5. Clear stored token                                       │
     │                                                              │
     │ 6. Redirect to /auth/signin                                 │
     │────────────────────────────────────────────────────────────>│
     │                                                              │
     │ 7. Show message: "Session expired, please sign in again"   │
     │────────────────────────────────────────────────────────────>│
     │                                                              │
```

### Frontend Implementation

```typescript
// frontend/lib/api.ts
export async function apiClient(endpoint: string, options: RequestInit = {}) {
  const token = await auth.getToken()

  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
      ...options.headers
    }
  })

  // Handle token expiration
  if (response.status === 401) {
    const error = await response.json()
    if (error.error.message.includes("expired")) {
      // Clear token and redirect to signin
      await auth.signOut()
      window.location.href = "/auth/signin?message=session_expired"
    }
  }

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error.message || "API request failed")
  }

  return response.json()
}
```

---

## 6. Security Considerations

### JWT Secret Management

**Requirements**:
- JWT secret must be at least 32 characters long
- Must be stored in environment variables (never in code)
- Must be identical between frontend and backend
- Should be rotated periodically (future enhancement)

**Environment Variables**:
```bash
# Backend (.env)
JWT_SECRET=your-super-secret-key-at-least-32-chars-long

# Frontend (.env.local)
BETTER_AUTH_SECRET=your-super-secret-key-at-least-32-chars-long
```

### Password Security

**Requirements** (FR-017):
- Passwords must be hashed using bcrypt
- Minimum cost factor: 12
- Never store plain text passwords
- Never log passwords

**Implementation**:
```python
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())
```

### User Isolation

**Requirements** (FR-010):
- All task queries must filter by user_id from JWT token
- Never trust user_id from request body or query parameters
- Always extract user_id from validated JWT token

**Implementation**:
```python
# backend/auth/dependencies.py
from fastapi import Depends, HTTPException
from uuid import UUID

async def get_current_user_id(token: str = Depends(verify_jwt_token)) -> UUID:
    """Extract user_id from validated JWT token"""
    return UUID(token)  # token is user_id from JWT sub claim

# backend/routes/tasks.py
@router.get("/tasks")
async def list_tasks(
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    statement = select(Task).where(Task.user_id == current_user_id)
    result = await session.execute(statement)
    return result.scalars().all()
```

---

## 7. Error Scenarios

| Scenario | HTTP Status | Error Code | User Action |
|----------|-------------|------------|-------------|
| Invalid email format | 400 | VALIDATION_ERROR | Correct email format |
| Password too short | 400 | VALIDATION_ERROR | Use longer password |
| Email already registered | 409 | CONFLICT | Use different email or sign in |
| Invalid credentials | 401 | UNAUTHORIZED | Check email/password |
| Missing token | 401 | UNAUTHORIZED | Sign in again |
| Invalid token | 401 | UNAUTHORIZED | Sign in again |
| Expired token | 401 | UNAUTHORIZED | Sign in again |
| Task not found | 404 | NOT_FOUND | Check task ID |

---

## Summary

**Authentication Method**: JWT-based token authentication with Better Auth

**Token Lifetime**: 24 hours

**Token Storage**: httpOnly cookies (XSS protection)

**User Isolation**: Enforced via user_id from JWT token

**Security**: Bcrypt password hashing (cost factor 12), JWT signature validation

**Error Handling**: Consistent error format with user-friendly messages

---

**Authentication Flow Status**: ✅ COMPLETE
**Date Completed**: 2026-01-13
**Next**: Create quickstart.md guide
