# Data Model

**Feature**: Todo Full-Stack Web Application (Basic Level)
**Date**: 2026-01-13
**Status**: Final

## Overview

This document defines the data model for Phase 2, including entity definitions, relationships, constraints, and validation rules. The model supports multi-user task management with strict user isolation.

## Entity Relationship Diagram

```
┌─────────────────┐
│      User       │
├─────────────────┤
│ id (PK)         │
│ email (UNIQUE)  │
│ password_hash   │
│ created_at      │
│ updated_at      │
└────────┬────────┘
         │
         │ 1:N
         │
         ▼
┌─────────────────┐
│      Task       │
├─────────────────┤
│ id (PK)         │
│ user_id (FK)    │◄─── Foreign Key to User.id
│ title           │
│ description     │
│ status          │
│ created_at      │
│ updated_at      │
└─────────────────┘
```

## Entities

### 1. User

Represents an authenticated user account with secure credentials.

**Table Name**: `user`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, NOT NULL | Unique identifier for the user |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | User's email address (used for login) |
| `password_hash` | VARCHAR(255) | NOT NULL | Bcrypt-hashed password (never store plain text) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**:
- Primary key index on `id` (automatic)
- Unique index on `email` for fast lookup during authentication

**Validation Rules**:
- **FR-001**: Email must be valid format (RFC 5322)
- **FR-017**: Password must be hashed using bcrypt (min cost factor 12)
- Email must be unique across all users
- Email is case-insensitive (normalize to lowercase before storage)

**Business Rules**:
- Users cannot be deleted if they have associated tasks (enforce referential integrity)
- Email cannot be changed after account creation (Phase 2 scope)
- Password changes require current password verification (out of scope for Phase 2)

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4

class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255, sa_column_kwargs={"nullable": False})
    password_hash: str = Field(max_length=255, sa_column_kwargs={"nullable": False})
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"nullable": False})
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"nullable": False})

    class Config:
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "created_at": "2026-01-13T10:00:00Z",
                "updated_at": "2026-01-13T10:00:00Z"
            }
        }
```

---

### 2. Task

Represents a todo item owned by a specific user.

**Table Name**: `task`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, NOT NULL | Unique identifier for the task |
| `user_id` | UUID | FOREIGN KEY (user.id), NOT NULL, INDEX | Owner of the task |
| `title` | VARCHAR(200) | NOT NULL | Task title (required) |
| `description` | VARCHAR(2000) | NULL | Optional task description |
| `status` | ENUM('pending', 'completed') | NOT NULL, DEFAULT 'pending' | Task completion status |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Task creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**:
- Primary key index on `id` (automatic)
- Index on `user_id` for efficient user-specific queries
- Composite index on `(user_id, status)` for filtered queries

**Foreign Keys**:
- `user_id` references `user(id)` with `ON DELETE CASCADE`
  - When a user is deleted, all their tasks are automatically deleted

**Validation Rules**:
- **FR-012**: Title must not be empty (min length 1, max length 200)
- Description is optional but limited to 2000 characters
- Status must be one of: 'pending', 'completed'
- **FR-016**: Title and description must be sanitized to prevent XSS

**Business Rules**:
- **FR-010**: Users can only access their own tasks (enforce via `user_id` filter)
- Tasks default to 'pending' status when created
- Status can only transition between 'pending' and 'completed' (no other states)
- Timestamps are automatically updated on modification

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"

class Task(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True, sa_column_kwargs={"nullable": False})
    title: str = Field(min_length=1, max_length=200, sa_column_kwargs={"nullable": False})
    description: str | None = Field(default=None, max_length=2000)
    status: TaskStatus = Field(default=TaskStatus.PENDING, sa_column_kwargs={"nullable": False})
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"nullable": False})
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"nullable": False})

    class Config:
        schema_extra = {
            "example": {
                "id": "660e8400-e29b-41d4-a716-446655440001",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Complete project documentation",
                "description": "Write comprehensive docs for Phase 2",
                "status": "pending",
                "created_at": "2026-01-13T10:00:00Z",
                "updated_at": "2026-01-13T10:00:00Z"
            }
        }
```

---

## Relationships

### User → Task (One-to-Many)

- **Cardinality**: One user can have zero or many tasks
- **Ownership**: Each task belongs to exactly one user
- **Cascade**: Deleting a user deletes all their tasks (ON DELETE CASCADE)
- **Isolation**: Tasks are strictly isolated by user_id (no cross-user access)

**Query Pattern**:
```python
# Get all tasks for a user
async def get_user_tasks(user_id: UUID, session: AsyncSession):
    statement = select(Task).where(Task.user_id == user_id)
    result = await session.execute(statement)
    return result.scalars().all()
```

---

## State Transitions

### Task Status State Machine

```
┌─────────┐
│ pending │◄────┐
└────┬────┘     │
     │          │
     │ toggle   │ toggle
     │          │
     ▼          │
┌───────────┐   │
│ completed │───┘
└───────────┘
```

**Valid Transitions**:
- `pending` → `completed`: User marks task as done
- `completed` → `pending`: User reopens task

**Invalid Transitions**:
- No other states exist in Phase 2
- Cannot transition to same state (idempotent operation)

**Implementation**:
```python
async def toggle_task_status(task_id: UUID, user_id: UUID, session: AsyncSession):
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Toggle status
    task.status = TaskStatus.COMPLETED if task.status == TaskStatus.PENDING else TaskStatus.PENDING
    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task
```

---

## Database Schema (SQL DDL)

```sql
-- Create UUID extension (if not exists)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create User table
CREATE TABLE "user" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create index on email for fast lookups
CREATE INDEX idx_user_email ON "user"(email);

-- Create Task status enum
CREATE TYPE task_status AS ENUM ('pending', 'completed');

-- Create Task table
CREATE TABLE task (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description VARCHAR(2000),
    status task_status NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes for efficient queries
CREATE INDEX idx_task_user_id ON task(user_id);
CREATE INDEX idx_task_user_status ON task(user_id, status);

-- Add check constraint for title length
ALTER TABLE task ADD CONSTRAINT chk_task_title_not_empty CHECK (LENGTH(title) > 0);
```

---

## Data Validation

### Input Validation (Pydantic Schemas)

**User Registration**:
```python
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr  # Validates email format
    password: str = Field(min_length=8, max_length=100)  # Password requirements

class UserResponse(BaseModel):
    id: UUID
    email: str
    created_at: datetime

    class Config:
        from_attributes = True
```

**Task Operations**:
```python
class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)

class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)

class TaskResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: str | None
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

### Security Validation

**XSS Prevention** (FR-016):
```python
import html

def sanitize_input(text: str) -> str:
    """Escape HTML entities to prevent XSS attacks"""
    return html.escape(text)

# Apply to all user inputs before storage
task.title = sanitize_input(task_create.title)
task.description = sanitize_input(task_create.description) if task_create.description else None
```

**User Isolation** (FR-010):
```python
# Always filter by user_id from JWT token
async def get_task(task_id: UUID, current_user_id: UUID, session: AsyncSession):
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user_id  # Critical: enforce user isolation
    )
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task
```

---

## Migration Strategy

### Initial Migration (Alembic)

```bash
# Initialize Alembic
alembic init alembic

# Generate initial migration
alembic revision --autogenerate -m "Initial schema: User and Task tables"

# Apply migration
alembic upgrade head
```

### Future Migrations

For Phase 3+ enhancements:
- Add `category` field to Task
- Add `due_date` field to Task
- Add `priority` field to Task
- Add `shared_with` table for task sharing

---

## Performance Considerations

### Query Optimization

1. **Index on user_id**: Ensures fast filtering of tasks by user
2. **Composite index on (user_id, status)**: Optimizes filtered queries (e.g., "show pending tasks")
3. **Email index**: Speeds up authentication lookups

### Expected Query Patterns

```python
# Most common query: Get all tasks for user (uses idx_task_user_id)
SELECT * FROM task WHERE user_id = ?

# Filtered query: Get pending tasks for user (uses idx_task_user_status)
SELECT * FROM task WHERE user_id = ? AND status = 'pending'

# Authentication: Find user by email (uses idx_user_email)
SELECT * FROM "user" WHERE email = ?
```

### Connection Pooling

```python
# backend/database.py
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Disable in production
    pool_size=10,  # Max 10 connections
    max_overflow=20,  # Allow 20 overflow connections
    pool_pre_ping=True  # Verify connections before use
)
```

---

## Data Integrity

### Referential Integrity

- Foreign key constraint ensures every task has a valid user
- CASCADE delete ensures orphaned tasks are removed when user is deleted

### Consistency Rules

- Timestamps are automatically managed (created_at, updated_at)
- Status enum ensures only valid states
- Title cannot be empty (check constraint)

### Concurrency Handling

- Use optimistic locking for updates (check updated_at timestamp)
- Database-level constraints prevent race conditions
- Transactions ensure atomic operations

---

## Summary

| Entity | Purpose | Key Constraints |
|--------|---------|-----------------|
| User | Authentication and ownership | Unique email, hashed password |
| Task | Todo items | User isolation, non-empty title, status enum |

**Relationships**: User (1) → (N) Task with CASCADE delete

**Security**: User isolation enforced at query level, XSS prevention via input sanitization

**Performance**: Indexes on user_id, email, and (user_id, status) for optimal query performance

---

**Data Model Status**: ✅ COMPLETE
**Date Completed**: 2026-01-13
**Next**: Generate API contracts (openapi.yaml, auth-flow.md)
