"""Create task function tool for OpenAI Agents SDK.

This tool enables the AI agent to create new todo tasks for users.
"""

import json
from typing import Optional
from uuid import UUID

from agents import function_tool
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import async_session_maker
from tools import format_error_response, format_success_response, sanitize_input


class CreateTaskInput(BaseModel):
    """Input parameters for creating a task."""

    user_id: str = Field(..., description="User UUID")
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(
        None, max_length=2000, description="Optional task description"
    )


@function_tool
async def create_task(params: CreateTaskInput) -> str:
    """Create a new todo task for the user.

    This function creates a new task with the provided title and optional description.
    The task is created in 'pending' status by default.

    Args:
        params: Task creation parameters including user_id, title, and optional description.

    Returns:
        JSON string with task creation result including task ID and title.
    """
    try:
        # Sanitize inputs to prevent XSS
        title = sanitize_input(params.title)
        description = sanitize_input(params.description) if params.description else None

        # Validate title length
        if len(title) < 1 or len(title) > 200:
            return format_error_response(
                "Task title must be between 1 and 200 characters", "INVALID_INPUT"
            )

        # Validate description length
        if description and len(description) > 2000:
            return format_error_response(
                "Task description must be 2000 characters or less", "INVALID_INPUT"
            )

        # Create database session
        async with async_session_maker() as session:
            # Import Task model (assuming it exists from Phase 2)
            # Note: This assumes Phase 2 Task model is available
            # If not, we'll need to create it or import from Phase 2
            from models import Task  # This will need to be added to models.py

            # Create new task
            task = Task(
                user_id=UUID(params.user_id),
                title=title,
                description=description,
                status="pending",
            )

            session.add(task)
            await session.commit()
            await session.refresh(task)

            # Return success response
            return format_success_response(
                {
                    "task": {
                        "id": str(task.id),
                        "title": task.title,
                        "description": task.description,
                        "status": task.status,
                    },
                    "message": f"Task '{task.title}' created successfully",
                }
            )

    except ValueError as e:
        return format_error_response(f"Invalid user ID format: {str(e)}", "INVALID_USER_ID")
    except Exception as e:
        return format_error_response(
            f"Failed to create task: {str(e)}", "TASK_CREATION_FAILED"
        )
