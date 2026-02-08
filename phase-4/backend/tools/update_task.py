"""Update task function tool for OpenAI Agents SDK.

This tool enables the AI agent to update task title and description.
"""

from typing import Optional
from uuid import UUID

from agents import function_tool
from pydantic import BaseModel, Field
from sqlalchemy import select

from database import async_session_maker
from tools import format_error_response, format_success_response, sanitize_input


class UpdateTaskInput(BaseModel):
    """Input parameters for updating a task."""

    user_id: str = Field(..., description="User UUID")
    task_id: str = Field(..., description="Task UUID to update")
    title: Optional[str] = Field(
        None, min_length=1, max_length=200, description="New task title"
    )
    description: Optional[str] = Field(
        None, max_length=2000, description="New task description"
    )


@function_tool
async def update_task(params: UpdateTaskInput) -> str:
    """Update a task's title and/or description.

    This function updates the specified task with new title and/or description.
    At least one field (title or description) must be provided.

    Args:
        params: Parameters including user_id, task_id, and optional title/description.

    Returns:
        JSON string with updated task details.
    """
    try:
        # Validate that at least one field is provided
        if not params.title and params.description is None:
            return format_error_response(
                "At least one field (title or description) must be provided",
                "NO_FIELDS_PROVIDED",
            )

        # Sanitize inputs
        title = sanitize_input(params.title) if params.title else None
        description = (
            sanitize_input(params.description) if params.description else None
        )

        # Validate lengths
        if title and (len(title) < 1 or len(title) > 200):
            return format_error_response(
                "Task title must be between 1 and 200 characters", "INVALID_INPUT"
            )

        if description and len(description) > 2000:
            return format_error_response(
                "Task description must be 2000 characters or less", "INVALID_INPUT"
            )

        # Create database session
        async with async_session_maker() as session:
            # Import Task model
            from models import Task

            # Find task with ownership verification
            statement = select(Task).where(
                Task.id == UUID(params.task_id),
                Task.user_id == UUID(params.user_id),
            )
            result = await session.execute(statement)
            task = result.scalar_one_or_none()

            if not task:
                return format_error_response(
                    "Task not found or you don't have permission to access it",
                    "TASK_NOT_FOUND",
                )

            # Update fields
            if title:
                task.title = title
            if description is not None:
                task.description = description

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
                    "message": f"Task '{task.title}' updated successfully",
                }
            )

    except ValueError as e:
        return format_error_response(f"Invalid ID format: {str(e)}", "INVALID_ID")
    except Exception as e:
        return format_error_response(
            f"Failed to update task: {str(e)}", "UPDATE_FAILED"
        )
