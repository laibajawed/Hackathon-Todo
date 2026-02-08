"""Toggle task status function tool for OpenAI Agents SDK.

This tool enables the AI agent to toggle task status between pending and completed.
"""

from uuid import UUID

from agents import function_tool
from pydantic import BaseModel, Field
from sqlalchemy import select

from database import async_session_maker
from tools import format_error_response, format_success_response


class ToggleTaskStatusInput(BaseModel):
    """Input parameters for toggling task status."""

    user_id: str = Field(..., description="User UUID")
    task_id: str = Field(..., description="Task UUID to toggle")


@function_tool
async def toggle_task_status(params: ToggleTaskStatusInput) -> str:
    """Toggle a task's status between pending and completed.

    This function finds the specified task and toggles its status.
    Pending tasks become completed, and completed tasks become pending.

    Args:
        params: Parameters including user_id and task_id.

    Returns:
        JSON string with updated task status.
    """
    try:
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

            # Toggle status
            old_status = task.status
            task.status = "completed" if task.status == "pending" else "pending"

            session.add(task)
            await session.commit()
            await session.refresh(task)

            # Return success response
            return format_success_response(
                {
                    "task": {
                        "id": str(task.id),
                        "title": task.title,
                        "status": task.status,
                    },
                    "message": f"Task '{task.title}' marked as {task.status}",
                    "previous_status": old_status,
                }
            )

    except ValueError as e:
        return format_error_response(f"Invalid ID format: {str(e)}", "INVALID_ID")
    except Exception as e:
        return format_error_response(
            f"Failed to toggle task status: {str(e)}", "TOGGLE_FAILED"
        )
