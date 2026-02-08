# Data Model: Todo AI Chatbot

**Feature**: 001-todo-ai-chatbot
**Date**: 2026-01-23
**Status**: Design Phase

## Overview

This document defines the data entities for the Todo AI Chatbot feature, extending the existing Phase 2 data model with conversation and message tracking capabilities.

---

## Entity Definitions

### 1. Conversation

Represents a chat session between a user and the AI assistant.

**Purpose**: Track conversation sessions, manage context, and enable session-based cleanup.

**Lifecycle**: Created on first message, persists during session, deleted on logout.

**Attributes:**

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique conversation identifier |
| user_id | Integer | Foreign Key (users.id), NOT NULL, Indexed | Owner of the conversation |
| title | String(255) | NOT NULL, Default: "New Conversation" | Conversation title (can be auto-generated from first message) |
| created_at | DateTime | NOT NULL, Default: UTC now | Conversation creation timestamp |
| updated_at | DateTime | NOT NULL, Default: UTC now | Last message timestamp |
| is_active | Boolean | NOT NULL, Default: true, Indexed | Whether conversation is currently active |
| total_tokens | Integer | NOT NULL, Default: 0 | Cumulative token count for context management |
| message_count | Integer | NOT NULL, Default: 0 | Quick message count without query |

**Relationships:**
- **User**: Many-to-One (Conversation belongs to User)
- **Messages**: One-to-Many (Conversation has many Messages, cascade delete)

**Indexes:**
- Primary: `id`
- Composite: `(user_id, is_active)` - Fast lookup of active conversation per user
- Single: `user_id` - Foreign key index

**Constraints:**
- One active conversation per user at a time (enforced at application level)
- Cascade delete: Deleting conversation deletes all associated messages

**Validation Rules:**
- `user_id` must reference existing user
- `title` cannot be empty
- `total_tokens` >= 0
- `message_count` >= 0
- `is_active` must be boolean

**State Transitions:**
```
[Created] → is_active = true
[New Conversation Started] → Previous conversation: is_active = false
[Logout] → [Deleted] (cascade deletes messages)
```

---

### 2. Message

Represents a single message in a conversation (user, assistant, or system).

**Purpose**: Store conversation history, enable context retrieval, track token usage.

**Lifecycle**: Created when message sent/received, persists with conversation, deleted on logout.

**Attributes:**

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique message identifier |
| conversation_id | Integer | Foreign Key (conversations.id), NOT NULL, Indexed | Parent conversation |
| role | Enum | NOT NULL, Values: 'user', 'assistant', 'system', Indexed | Message sender role |
| content | Text | NOT NULL | Message content (unlimited length) |
| token_count | Integer | NOT NULL, Default: 0 | Estimated token count for this message |
| created_at | DateTime | NOT NULL, Default: UTC now | Message creation timestamp |
| sequence_number | Integer | NOT NULL, Default: 0 | Order within conversation (0-indexed) |

**Relationships:**
- **Conversation**: Many-to-One (Message belongs to Conversation)

**Indexes:**
- Primary: `id`
- Composite: `(conversation_id, sequence_number)` - Fast ordered retrieval
- Composite: `(conversation_id, created_at)` - Time-based queries
- Single: `conversation_id` - Foreign key index
- Single: `role` - Filter by role

**Constraints:**
- `conversation_id` must reference existing conversation
- `sequence_number` must be unique within conversation
- Cascade delete: Deleting conversation deletes all messages

**Validation Rules:**
- `role` must be one of: 'user', 'assistant', 'system'
- `content` cannot be empty
- `token_count` >= 0
- `sequence_number` >= 0
- `sequence_number` must be sequential within conversation

**Message Role Semantics:**
- **user**: Message from the human user
- **assistant**: Response from the AI assistant
- **system**: System prompts or instructions (not displayed to user)

---

## Existing Entities (Phase 2)

### 3. Task (Reference)

Existing entity from Phase 2, used by MCP tools.

**Attributes:**
- id: UUID, Primary Key
- user_id: Integer, Foreign Key (users.id)
- title: String(200), NOT NULL
- description: Text, Nullable
- status: Enum ('pending', 'completed')
- created_at: DateTime
- updated_at: DateTime

**Note**: No changes to Task entity. MCP tools operate on existing Task model.

### 4. User (Reference)

Existing entity from Phase 2, referenced by conversations.

**Attributes:**
- id: Integer, Primary Key
- email: String, Unique
- password_hash: String
- created_at: DateTime

**Note**: No changes to User entity.

---

## Database Schema (SQLModel)

### Conversation Model

```python
from sqlmodel import SQLModel, Field, Relationship, Index
from datetime import datetime
from typing import Optional, List

class Conversation(SQLModel, table=True):
    """
    Represents a chat session between user and AI assistant.
    Session-based: deleted on logout.
    """
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    title: str = Field(max_length=255, default="New Conversation")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True, index=True)
    total_tokens: int = Field(default=0, ge=0)
    message_count: int = Field(default=0, ge=0)

    # Relationships
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    # Indexes
    __table_args__ = (
        Index("idx_user_active", "user_id", "is_active"),
    )
```

### Message Model

```python
from sqlmodel import SQLModel, Field, Relationship, Index, Column, Text
from sqlalchemy import Text as SAText
from datetime import datetime
from typing import Optional
from enum import Enum

class MessageRole(str, Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class Message(SQLModel, table=True):
    """
    Represents a single message in a conversation.
    Optimized for sequential retrieval and token counting.
    """
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(
        foreign_key="conversations.id",
        nullable=False,
        index=True
    )
    role: MessageRole = Field(nullable=False, index=True)
    content: str = Field(sa_column=Column(SAText), nullable=False)
    token_count: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sequence_number: int = Field(default=0, ge=0)

    # Relationships
    conversation: Optional[Conversation] = Relationship(
        back_populates="messages"
    )

    # Indexes
    __table_args__ = (
        Index("idx_conversation_sequence", "conversation_id", "sequence_number"),
        Index("idx_conversation_created", "conversation_id", "created_at"),
    )
```

---

## Database Migration

### Alembic Migration Script

```python
"""Add conversation and message tables for AI chatbot

Revision ID: 002_add_conversations
Revises: 001_initial
Create Date: 2026-01-23
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('total_tokens', sa.Integer(), nullable=False),
        sa.Column('message_count', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_active', 'conversations', ['user_id', 'is_active'])
    op.create_index(op.f('ix_conversations_user_id'), 'conversations', ['user_id'])
    op.create_index(op.f('ix_conversations_is_active'), 'conversations', ['is_active'])

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('token_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('sequence_number', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['conversation_id'],
            ['conversations.id'],
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_conversation_sequence', 'messages', ['conversation_id', 'sequence_number'])
    op.create_index('idx_conversation_created', 'messages', ['conversation_id', 'created_at'])
    op.create_index(op.f('ix_messages_conversation_id'), 'messages', ['conversation_id'])
    op.create_index(op.f('ix_messages_role'), 'messages', ['role'])

def downgrade():
    op.drop_table('messages')
    op.drop_table('conversations')
```

---

## Query Patterns

### Common Queries

**1. Get Active Conversation for User:**
```python
statement = select(Conversation).where(
    Conversation.user_id == user_id,
    Conversation.is_active == True
)
conversation = session.exec(statement).first()
```
**Performance**: O(1) with `idx_user_active` composite index

**2. Get Recent Messages for Context:**
```python
statement = (
    select(Message)
    .where(Message.conversation_id == conversation_id)
    .order_by(Message.sequence_number.desc())
    .limit(50)
)
messages = session.exec(statement).all()
```
**Performance**: O(log n) with `idx_conversation_sequence` index

**3. Get Messages Within Token Budget:**
```python
statement = (
    select(Message)
    .where(Message.conversation_id == conversation_id)
    .order_by(Message.sequence_number.desc())
)

messages = []
cumulative_tokens = 0
for message in session.exec(statement):
    if cumulative_tokens + message.token_count > max_tokens:
        break
    messages.append(message)
    cumulative_tokens += message.token_count

return list(reversed(messages))
```
**Performance**: O(n) but typically processes <50 messages

**4. Add Message to Conversation:**
```python
# Get next sequence number
count = session.exec(
    select(func.count(Message.id))
    .where(Message.conversation_id == conversation_id)
).one()

message = Message(
    conversation_id=conversation_id,
    role=role,
    content=content,
    token_count=token_count,
    sequence_number=count
)
session.add(message)

# Update conversation metadata
conversation.message_count += 1
conversation.total_tokens += token_count
conversation.updated_at = datetime.utcnow()
session.add(conversation)

session.commit()
```
**Performance**: O(1) with proper indexes

**5. Delete All User Conversations (Logout):**
```python
statement = select(Conversation).where(Conversation.user_id == user_id)
conversations = session.exec(statement).all()

for conversation in conversations:
    session.delete(conversation)  # Cascade deletes messages

session.commit()
```
**Performance**: O(n) where n = number of conversations (typically 1)

---

## Data Integrity

### Referential Integrity

- **Conversation → User**: ON DELETE CASCADE (deleting user deletes conversations)
- **Message → Conversation**: ON DELETE CASCADE (deleting conversation deletes messages)

### Application-Level Constraints

- **One Active Conversation**: Enforced by deactivating previous conversation when creating new one
- **Sequential Sequence Numbers**: Enforced by querying count before insert
- **Token Count Accuracy**: Calculated using tiktoken library before insert

### Validation

- All NOT NULL constraints enforced at database level
- Enum values validated by SQLModel
- Foreign key constraints enforced by database
- Index constraints ensure query performance

---

## Performance Considerations

### Index Strategy

**Critical Indexes:**
1. `idx_user_active (user_id, is_active)` - Enables O(1) active conversation lookup
2. `idx_conversation_sequence (conversation_id, sequence_number)` - Fast ordered message retrieval
3. `idx_conversation_created (conversation_id, created_at)` - Time-based queries

**Index Maintenance:**
- Indexes automatically maintained by PostgreSQL
- Analyze tables periodically: `ANALYZE conversations; ANALYZE messages;`
- Monitor index usage: `pg_stat_user_indexes`

### Connection Pooling

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,        # 100 concurrent users / 5 avg queries = 20
    max_overflow=10,     # Burst capacity
    pool_pre_ping=True,  # Verify connections
    pool_recycle=3600    # Recycle hourly
)
```

### Query Optimization

- Use `LIMIT` for message retrieval (default: 50)
- Specify columns instead of `SELECT *`
- Use indexed columns in WHERE clauses
- Avoid N+1 queries with eager loading

---

## Storage Estimates

### Per Conversation

- Conversation record: ~100 bytes
- Average message: ~500 bytes (including content)
- 30 messages per conversation: ~15 KB
- 100 concurrent users: ~1.5 MB active data

### Cleanup Strategy

- Session-based: All data deleted on logout
- No long-term storage accumulation
- Database size remains constant

---

## Security Considerations

### User Isolation

- All queries filter by `user_id`
- JWT validation ensures user identity
- No cross-user data access possible

### Data Sanitization

- HTML escape all user input before storage
- Prevent XSS attacks in message content
- Validate message length limits

### Audit Trail

- `created_at` and `updated_at` timestamps
- Sequence numbers enable message ordering verification
- Token counts enable usage tracking

---

## Summary

The data model extends Phase 2 with two new entities (Conversation, Message) optimized for:
- Fast conversation lookup (composite indexes)
- Efficient message retrieval (sequence-based ordering)
- Token-aware context management (token_count tracking)
- Session-based lifecycle (cascade deletes)
- 100 concurrent user scalability (connection pooling)

All design decisions support the <1 second query performance requirement and session-based conversation model.
