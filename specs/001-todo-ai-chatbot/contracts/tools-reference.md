# Function Tools Reference: Todo AI Chatbot

**Feature**: 001-todo-ai-chatbot
**Date**: 2026-01-26
**Status**: Design Phase

## Overview

This document defines the 5 function tools that enable the AI agent to manage todo tasks through natural language. All tools use the `@function_tool` decorator from OpenAI Agents SDK with automatic schema generation from Pydantic models.

---

## Tool Architecture Principles

### Stateless Design
- Each tool call is independent
- Database is the source of truth
- No internal state maintained between calls
- New database session created per invocation

### User Isolation
- All tools require `user_id` parameter
- Ownership verification before operations
- JWT validation at API layer (not in tools)

### Return Format
- All tools return JSON strings
- Success responses include operation results
- Error responses include error messages
- Consistent structure across all tools

---

## Tool 1: list_tasks

**Purpose**: Retrieve user's tasks with optional filtering

**Characteristics**: Read-only, idempotent, safe

### Input Model

```python
from pydantic import BaseModel, Field
from typing import Optional

class ListTasksInput(BaseModel):
    """Input parameters for listing tasks."""
    user_id: str = Field(description="User UUID")
    status: Optional[str] = Field(
        default=None,
        description="Filter by status: 'pending' or 'completed'. Omit to return all tasks."
    )
    limit: Optional[int] = Field(
        default=50,
        description="Maximum number of tasks to return",
        ge=1,
        le=100
    )
```

### Tool Definition

```python
from agents import function_tool
from sqlmodel import select
from uuid import UUID
import json

@function_tool
async def list_tasks(params: ListTasksInput) -> str:
    """List all tasks for a user with optional status filtering.

    Args:
        params: Task listing parameters including user_id, optional status filter, and limit.

    Returns:
        JSON string containing task list with total count and task details.
    """
    async with async_session_maker() as session:
        # Build query
        statement = select(Task).where(Task.user_id == UUID(params.user_id))

        # Apply status filter if provided
        if params.status:
            statement = statement.where(Task.status == params.status)

        # Apply limit
        statement = statement.limit(params.limit)

        # Execute query
        result = await session.execute(statement)
        tasks = result.scalars().all()

        # Format response
        return json.dumps({
            "success": True,
            "total": len(tasks),
            "tasks": [
                {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                }
                for task in tasks
            ]
        })
```

### Example Invocations

**List all tasks:**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": null,
  "limit": 50
}
```

**List pending tasks only:**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "pending",
  "limit": 50
}
```

### Response Format

```json
{
  "success": true,
  "total": 3,
  "tasks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "status": "pending",
      "created_at": "2026-01-26T10:00:00",
      "updated_at": "2026-01-26T10:00:00"
    }
  ]
}
```

---

## Tool 2: create_task

**Purpose**: Create a new todo task

**Characteristics**: Non-idempotent, mutating

### Input Model

```python
from pydantic import BaseModel, Field
from typing import Optional

class CreateTaskInput(BaseModel):
    """Input parameters for creating a task."""
    user_id: str = Field(description="User UUID")
    title: str = Field(description="Task title", min_length=1, max_length=200)
    description: Optional[str] = Field(
        default=None,
        description="Optional task description"
    )
```

### Tool Definition

```python
from agents import function_tool
from uuid import UUID
import json
import html

@function_tool
async def create_task(params: CreateTaskInput) -> str:
    """Create a new todo task for the user.

    Args:
        params: Task creation parameters including user_id, title, and optional description.

    Returns:
        JSON string with created task details.
    """
    async with async_session_maker() as session:
        # Sanitize inputs
        title = html.escape(params.title)
        description = html.escape(params.description) if params.description else None

        # Create task
        task = Task(
            user_id=UUID(params.user_id),
            title=title,
            description=description,
            status="pending"
        )

        session.add(task)
        await session.commit()
        await session.refresh(task)

        # Return success response
        return json.dumps({
            "success": True,
            "message": f"Task '{task.title}' created successfully",
            "task": {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "created_at": task.created_at.isoformat()
            }
        })
```

### Example Invocation

```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

### Response Format

```json
{
  "success": true,
  "message": "Task 'Buy groceries' created successfully",
  "task": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "status": "pending",
    "created_at": "2026-01-26T10:00:00"
  }
}
```

---

## Tool 3: update_task

**Purpose**: Update task title and/or description

**Characteristics**: Idempotent, mutating

### Input Model

```python
from pydantic import BaseModel, Field
from typing import Optional

class UpdateTaskInput(BaseModel):
    """Input parameters for updating a task."""
    user_id: str = Field(description="User UUID")
    task_id: str = Field(description="Task UUID to update")
    title: Optional[str] = Field(
        default=None,
        description="New task title",
        min_length=1,
        max_length=200
    )
    description: Optional[str] = Field(
        default=None,
        description="New task description"
    )
```

### Tool Definition

```python
from agents import function_tool
from sqlmodel import select
from uuid import UUID
import json
import html

@function_tool
async def update_task(params: UpdateTaskInput) -> str:
    """Update an existing task's title and/or description.

    Args:
        params: Task update parameters including user_id, task_id, and fields to update.

    Returns:
        JSON string with updated task details or error message.
    """
    async with async_session_maker() as session:
        # Verify ownership and get task
        statement = select(Task).where(
            Task.id == UUID(params.task_id),
            Task.user_id == UUID(params.user_id)
        )
        result = await session.execute(statement)
        task = result.scalar_one_or_none()

        if not task:
            return json.dumps({
                "success": False,
                "error": "Task not found or you don't have permission to update it"
            })

        # Update fields if provided
        if params.title:
            task.title = html.escape(params.title)

        if params.description is not None:
            task.description = html.escape(params.description) if params.description else None

        await session.commit()
        await session.refresh(task)

        return json.dumps({
            "success": True,
            "message": f"Task '{task.title}' updated successfully",
            "task": {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "updated_at": task.updated_at.isoformat()
            }
        })
```

### Example Invocation

```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy organic groceries",
  "description": "Organic milk, free-range eggs, whole grain bread"
}
```

### Response Format

```json
{
  "success": true,
  "message": "Task 'Buy organic groceries' updated successfully",
  "task": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy organic groceries",
    "description": "Organic milk, free-range eggs, whole grain bread",
    "status": "pending",
    "updated_at": "2026-01-26T11:00:00"
  }
}
```

---

## Tool 4: toggle_task_status

**Purpose**: Toggle task between pending and completed

**Characteristics**: Non-idempotent, mutating

### Input Model

```python
from pydantic import BaseModel, Field

class ToggleTaskStatusInput(BaseModel):
    """Input parameters for toggling task status."""
    user_id: str = Field(description="User UUID")
    task_id: str = Field(description="Task UUID to toggle")
```

### Tool Definition

```python
from agents import function_tool
from sqlmodel import select
from uuid import UUID
import json

@function_tool
async def toggle_task_status(params: ToggleTaskStatusInput) -> str:
    """Toggle a task's status between pending and completed.

    Args:
        params: Task toggle parameters including user_id and task_id.

    Returns:
        JSON string with updated task status or error message.
    """
    async with async_session_maker() as session:
        # Verify ownership and get task
        statement = select(Task).where(
            Task.id == UUID(params.task_id),
            Task.user_id == UUID(params.user_id)
        )
        result = await session.execute(statement)
        task = result.scalar_one_or_none()

        if not task:
            return json.dumps({
                "success": False,
                "error": "Task not found or you don't have permission to modify it"
            })

        # Toggle status
        old_status = task.status
        task.status = "completed" if task.status == "pending" else "pending"

        await session.commit()
        await session.refresh(task)

        return json.dumps({
            "success": True,
            "message": f"Task '{task.title}' marked as {task.status}",
            "task": {
                "id": str(task.id),
                "title": task.title,
                "status": task.status,
                "previous_status": old_status,
                "updated_at": task.updated_at.isoformat()
            }
        })
```

### Example Invocation

```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Response Format

```json
{
  "success": true,
  "message": "Task 'Buy groceries' marked as completed",
  "task": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries",
    "status": "completed",
    "previous_status": "pending",
    "updated_at": "2026-01-26T12:00:00"
  }
}
```

---

## Tool 5: delete_task

**Purpose**: Permanently delete a task

**Characteristics**: Destructive, idempotent

### Input Model

```python
from pydantic import BaseModel, Field

class DeleteTaskInput(BaseModel):
    """Input parameters for deleting a task."""
    user_id: str = Field(description="User UUID")
    task_id: str = Field(description="Task UUID to delete")
```

### Tool Definition

```python
from agents import function_tool
from sqlmodel import select
from uuid import UUID
import json

@function_tool
async def delete_task(params: DeleteTaskInput) -> str:
    """Permanently delete a task.

    Args:
        params: Task deletion parameters including user_id and task_id.

    Returns:
        JSON string confirming deletion or error message.
    """
    async with async_session_maker() as session:
        # Verify ownership and get task
        statement = select(Task).where(
            Task.id == UUID(params.task_id),
            Task.user_id == UUID(params.user_id)
        )
        result = await session.execute(statement)
        task = result.scalar_one_or_none()

        if not task:
            return json.dumps({
                "success": False,
                "error": "Task not found or you don't have permission to delete it"
            })

        # Store title for confirmation message
        task_title = task.title

        # Delete task
        await session.delete(task)
        await session.commit()

        return json.dumps({
            "success": True,
            "message": f"Task '{task_title}' deleted successfully",
            "deleted_task_id": params.task_id
        })
```

### Example Invocation

```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Response Format

```json
{
  "success": true,
  "message": "Task 'Buy groceries' deleted successfully",
  "deleted_task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Error Handling

### Common Error Responses

**Task Not Found:**
```json
{
  "success": false,
  "error": "Task not found or you don't have permission to access it"
}
```

**Invalid UUID:**
```json
{
  "success": false,
  "error": "Invalid UUID format for user_id or task_id"
}
```

**Database Error:**
```json
{
  "success": false,
  "error": "Database operation failed. Please try again."
}
```

### Error Handling Pattern

```python
@function_tool
async def example_tool(params: ExampleInput) -> str:
    try:
        async with async_session_maker() as session:
            # Tool implementation
            pass
    except ValueError as e:
        return json.dumps({
            "success": False,
            "error": f"Invalid input: {str(e)}"
        })
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return json.dumps({
            "success": False,
            "error": "An unexpected error occurred. Please try again."
        })
```

---

## Agent Integration

### Tool Registration

```python
from agents import Agent
from agents.extensions.models.litellm_model import LitellmModel
from tools import list_tasks, create_task, update_task, toggle_task_status, delete_task

agent = Agent(
    name="Todo Assistant",
    instructions="""You help users manage their todo tasks through natural language.

Tool Usage Guidelines:
- Use list_tasks to show users their tasks
- Use create_task when users want to add new tasks
- Use update_task when users want to modify task details
- Use toggle_task_status when users mark tasks complete or incomplete
- Use delete_task when users want to remove tasks permanently

Always confirm destructive operations (delete) before executing.
Provide clear, friendly feedback after each operation.""",
    model=LitellmModel(
        model="groq/llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY")
    ),
    tools=[list_tasks, create_task, update_task, toggle_task_status, delete_task]
)
```

### Execution Flow

1. User sends natural language message
2. OpenAI Agents SDK passes message to Groq via LiteLLM
3. Groq interprets intent and returns tool_calls
4. SDK automatically executes @function_tool decorated functions
5. Tool results added to conversation context
6. SDK calls Groq again with tool results
7. Groq generates natural language response
8. Response returned to user

---

## Testing Considerations

### Unit Tests

Test each tool independently:
- Valid inputs with expected outputs
- Invalid user_id (ownership verification)
- Invalid task_id (not found scenarios)
- Edge cases (empty strings, special characters)
- Database errors (connection failures)

### Integration Tests

Test tool invocation through OpenAI Agents SDK:
- Agent correctly interprets natural language intent
- Tools are invoked with correct parameters
- Tool results are properly formatted
- Agent generates appropriate responses

### Example Test

```python
import pytest
from tools import create_task, CreateTaskInput

@pytest.mark.asyncio
async def test_create_task_success():
    params = CreateTaskInput(
        user_id="123e4567-e89b-12d3-a456-426614174000",
        title="Test task",
        description="Test description"
    )

    result = await create_task(params)
    result_dict = json.loads(result)

    assert result_dict["success"] is True
    assert result_dict["task"]["title"] == "Test task"
    assert result_dict["task"]["status"] == "pending"
```

---

## Summary

All 5 function tools follow consistent patterns:
- Pydantic models for type-safe input validation
- @function_tool decorator for automatic schema generation
- Stateless design with database as source of truth
- User isolation through ownership verification
- JSON string responses with consistent structure
- Comprehensive error handling
- HTML escaping for XSS prevention

These tools enable the AI agent to perform all basic todo operations through natural language conversation while maintaining security, reliability, and user isolation.
