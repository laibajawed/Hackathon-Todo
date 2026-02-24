"""
Database models for User and Task entities.
Uses SQLModel for ORM with Pydantic validation.
Extended with Conversation and Message models for Phase 3 chatbot.
"""
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Index, Text
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from typing import Optional, List


class TaskStatus(str, Enum):
    """Task completion status enum."""
    PENDING = "pending"
    COMPLETED = "completed"


class TaskPriority(str, Enum):
    """Task priority level enum."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class User(SQLModel, table=True):
    """
    User model for authentication and task ownership.

    Attributes:
        id: Unique user identifier (UUID)
        email: User's email address (unique, used for login)
        password_hash: Bcrypt-hashed password (never store plain text)
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "user"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255, sa_column_kwargs={"nullable": False})
    password_hash: str = Field(max_length=255, sa_column_kwargs={"nullable": False})
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"nullable": False})
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"nullable": False})


class Task(SQLModel, table=True):
    """
    Task model for todo items.

    Attributes:
        id: Unique task identifier (UUID)
        user_id: Foreign key to User.id (owner of the task)
        title: Task title (required, max 200 chars)
        description: Optional task description (max 1000 chars)
        priority: Task priority level (low, medium, high)
        tag: Optional task tag (max 50 chars)
        status: Task completion status (pending or completed)
        created_at: Task creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "task"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True, sa_column_kwargs={"nullable": False})
    title: str = Field(min_length=1, max_length=200, sa_column_kwargs={"nullable": False})
    description: Optional[str] = Field(default=None, max_length=1000)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, sa_column_kwargs={"nullable": False})
    tag: Optional[str] = Field(default=None, max_length=50)
    status: TaskStatus = Field(default=TaskStatus.PENDING, sa_column_kwargs={"nullable": False})
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"nullable": False})
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"nullable": False})


class MessageRole(str, Enum):
    """Message role enumeration for conversation participants."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Conversation(SQLModel, table=True):
    """Represents a chat session between user and AI assistant.

    Lifecycle: Created on first message, persists during session, deleted on logout.
    One active conversation per user at a time (enforced at application level).
    """
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", nullable=False, index=True)
    title: str = Field(max_length=255, default="New Conversation")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True, index=True)
    total_tokens: int = Field(default=0, ge=0)
    message_count: int = Field(default=0, ge=0)

    # Relationships
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    # Indexes
    __table_args__ = (Index("idx_user_active", "user_id", "is_active"),)


class Message(SQLModel, table=True):
    """Represents a single message in a conversation.

    Optimized for sequential retrieval and token counting.
    Messages are ordered by sequence_number within each conversation.
    """
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(
        foreign_key="conversations.id", nullable=False, index=True
    )
    role: MessageRole = Field(nullable=False, index=True)
    content: str = Field(sa_column=Column(Text, nullable=False))
    token_count: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sequence_number: int = Field(default=0, ge=0)

    # Relationships
    conversation: Optional[Conversation] = Relationship(back_populates="messages")

    # Indexes
    __table_args__ = (
        Index("idx_conversation_sequence", "conversation_id", "sequence_number"),
        Index("idx_conversation_created", "conversation_id", "created_at"),
    )

