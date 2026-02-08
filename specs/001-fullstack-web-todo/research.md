# Research & Technology Validation

**Feature**: Todo Full-Stack Web Application (Basic Level)
**Date**: 2026-01-13
**Status**: Completed

## Overview

This document captures research findings and technology validation for Phase 2 implementation. All decisions are based on the technical stack specified in the project constitution and feature requirements.

## 1. Better Auth Integration with FastAPI

### Research Question
How to validate Better Auth JWT tokens in FastAPI middleware and share JWT secrets between Next.js frontend and FastAPI backend?

### Decision
Use standard JWT validation libraries (PyJWT) in FastAPI rather than Better Auth-specific libraries, as Better Auth is primarily a frontend authentication library.

### Rationale
- Better Auth generates standard JWT tokens that can be validated by any JWT library
- PyJWT is the industry-standard Python library for JWT validation
- FastAPI has excellent integration patterns with PyJWT via dependencies
- Separation of concerns: Better Auth handles frontend auth flow, FastAPI validates tokens

### Implementation Approach

**JWT Secret Sharing**:
- Store JWT secret in environment variables for both frontend and backend
- Frontend: `BETTER_AUTH_SECRET` in `.env.local`
- Backend: `JWT_SECRET` in `.env`
- Both must use the same secret value for token signing/validation

**Token Extraction**:
- Frontend sends JWT in `Authorization: Bearer <token>` header
- Backend extracts token from header using FastAPI dependency
- Validate token signature, expiration, and extract user claims

**Code Pattern**:
```python
# backend/auth/jwt.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime

security = HTTPBearer()

def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Alternatives Considered
- **Custom JWT implementation**: Rejected due to security risks and maintenance burden
- **OAuth2 password flow**: Rejected as Better Auth already handles authentication flow
- **Session-based auth**: Rejected due to REST API statelessness requirements

### References
- PyJWT documentation: https://pyjwt.readthedocs.io/
- FastAPI security documentation: https://fastapi.tiangolo.com/tutorial/security/
- Better Auth JWT plugin: https://www.better-auth.com/docs/plugins/jwt

---

## 2. Next.js 16+ App Router with Better Auth

### Research Question
How to set up Better Auth with Next.js 16+ App Router (not Pages Router) and implement protected routes?

### Decision
Use Better Auth with JWT plugin for Next.js App Router, storing tokens in httpOnly cookies for security.

### Rationale
- Better Auth has native support for Next.js App Router
- JWT plugin provides token-based authentication suitable for REST APIs
- httpOnly cookies prevent XSS attacks while maintaining usability
- App Router's server components enable server-side auth checks

### Implementation Approach

**Better Auth Setup**:
```typescript
// frontend/lib/auth.ts
import { betterAuth } from "better-auth/client"
import { jwtPlugin } from "better-auth/plugins"

export const auth = betterAuth({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  plugins: [
    jwtPlugin({
      secret: process.env.BETTER_AUTH_SECRET!,
      expiresIn: "24h"
    })
  ]
})
```

**Protected Routes Pattern**:
```typescript
// frontend/components/AuthGuard.tsx
"use client"
import { useAuth } from "@/hooks/useAuth"
import { useRouter } from "next/navigation"
import { useEffect } from "react"

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && !user) {
      router.push("/auth/signin")
    }
  }, [user, loading, router])

  if (loading) return <div>Loading...</div>
  if (!user) return null

  return <>{children}</>
}
```

**API Client with JWT**:
```typescript
// frontend/lib/api.ts
import { auth } from "./auth"

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

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.message || "API request failed")
  }

  return response.json()
}
```

### Alternatives Considered
- **NextAuth.js**: Rejected as Better Auth is specified in requirements
- **Client-side localStorage for tokens**: Rejected due to XSS vulnerability
- **Pages Router**: Rejected as App Router is specified in requirements

### References
- Better Auth documentation: https://www.better-auth.com/
- Next.js App Router authentication: https://nextjs.org/docs/app/building-your-application/authentication
- Next.js 16 documentation: https://nextjs.org/docs

---

## 3. SQLModel with Neon PostgreSQL

### Research Question
How to connect SQLModel to Neon PostgreSQL with proper async support and handle database migrations?

### Decision
Use SQLModel with async SQLAlchemy engine for Neon PostgreSQL, with Alembic for database migrations.

### Rationale
- SQLModel provides excellent FastAPI integration with Pydantic validation
- Neon requires SSL connections and supports standard PostgreSQL connection strings
- Async support is essential for FastAPI's async endpoints
- Alembic is the standard migration tool for SQLAlchemy-based projects

### Implementation Approach

**Neon Connection String Format**:
```
postgresql+asyncpg://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
```

**Database Configuration**:
```python
# backend/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
import os

DATABASE_URL = os.getenv("DATABASE_URL")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries in development
    future=True
)

# Create async session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

**Model Definition**:
```python
# backend/models.py
from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"

class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Task(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    title: str = Field(max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Migration Strategy**:
- Use Alembic for schema migrations
- Initialize with: `alembic init alembic`
- Configure `alembic.ini` with Neon connection string
- Generate migrations: `alembic revision --autogenerate -m "message"`
- Apply migrations: `alembic upgrade head`

### Alternatives Considered
- **SQLAlchemy Core without SQLModel**: Rejected as SQLModel provides better Pydantic integration
- **Synchronous database access**: Rejected as it blocks FastAPI's async event loop
- **Manual schema management**: Rejected as Alembic provides version control for schema changes

### References
- SQLModel documentation: https://sqlmodel.tiangolo.com/
- Neon PostgreSQL documentation: https://neon.tech/docs/
- Alembic documentation: https://alembic.sqlalchemy.org/
- asyncpg driver: https://github.com/MagicStack/asyncpg

---

## 4. CORS Configuration

### Research Question
How to configure CORS in FastAPI to allow Next.js frontend requests with JWT credentials?

### Decision
Use FastAPI's CORSMiddleware with explicit origin configuration and credentials support.

### Rationale
- CORS is required for browser-based frontend to call backend API on different port/domain
- Credentials support needed for httpOnly cookies (if used)
- Explicit origin configuration is more secure than wildcard in production
- FastAPI provides built-in CORS middleware

### Implementation Approach

**CORS Configuration**:
```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:3000",  # Next.js development server
    "http://localhost:3001",  # Alternative port
    # Add production frontend URL when deployed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

**Frontend Configuration**:
```typescript
// frontend/lib/api.ts
const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
  ...options,
  credentials: "include",  // Include cookies in requests
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`,
    ...options.headers
  }
})
```

### Alternatives Considered
- **Wildcard CORS (`allow_origins=["*"]`)**: Rejected as insecure for production
- **No CORS (same-origin deployment)**: Rejected as frontend and backend run on different ports in development
- **Proxy configuration**: Rejected as adds complexity without security benefits

### References
- FastAPI CORS documentation: https://fastapi.tiangolo.com/tutorial/cors/
- MDN CORS guide: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS

---

## 5. Development Environment Setup

### Research Question
How to run FastAPI backend and Next.js frontend concurrently in development with proper environment variable management?

### Decision
Use separate terminal sessions for backend and frontend with environment-specific `.env` files.

### Rationale
- Simple and transparent: developers can see logs from both services
- No additional tooling required (no docker-compose for development)
- Easy to restart individual services during development
- Clear separation of environment variables

### Implementation Approach

**Backend Setup**:
```bash
# Terminal 1: Backend
cd phase-2/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with actual values (DATABASE_URL, JWT_SECRET)
uvicorn main:app --reload --port 8000
```

**Frontend Setup**:
```bash
# Terminal 2: Frontend
cd phase-2/frontend
npm install
cp .env.local.example .env.local
# Edit .env.local with actual values (NEXT_PUBLIC_API_URL, BETTER_AUTH_SECRET)
npm run dev
```

**Environment Variables**:

Backend `.env`:
```
DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
JWT_SECRET=your-secret-key-here-must-match-frontend
ENVIRONMENT=development
```

Frontend `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-key-here-must-match-backend
```

**Hot Reload**:
- FastAPI: `--reload` flag enables auto-reload on code changes
- Next.js: Built-in Fast Refresh for instant updates

### Alternatives Considered
- **Docker Compose**: Rejected as adds complexity for local development (reserved for production)
- **Monorepo task runner (Turborepo, Nx)**: Rejected as overkill for two services
- **Concurrently npm package**: Rejected as separate terminals provide better visibility

### References
- FastAPI deployment: https://fastapi.tiangolo.com/deployment/
- Next.js environment variables: https://nextjs.org/docs/basic-features/environment-variables
- uvicorn documentation: https://www.uvicorn.org/

---

## Summary of Key Decisions

| Area | Decision | Key Rationale |
|------|----------|---------------|
| JWT Validation | PyJWT in FastAPI | Standard library, excellent FastAPI integration |
| Frontend Auth | Better Auth with JWT plugin | Native Next.js App Router support, secure token storage |
| Database | SQLModel + asyncpg + Alembic | Async support, Pydantic integration, migration management |
| CORS | FastAPI CORSMiddleware | Built-in, secure, supports credentials |
| Dev Environment | Separate terminals | Simple, transparent, no additional tooling |

## Unresolved Questions

None - all research tasks completed successfully.

## Next Steps

1. ✅ Research completed
2. **Next**: Generate data-model.md with entity definitions
3. **Next**: Generate API contracts (openapi.yaml, auth-flow.md)
4. **Next**: Create quickstart.md guide
5. **Next**: Update agent context with Phase 2 technologies

---

**Research Status**: ✅ COMPLETE
**Date Completed**: 2026-01-13
**Validated By**: Claude Code Agent
