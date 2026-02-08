"""Delete task function tool for OpenAI Agents SDK.

This tool enables the AI agent to permanently delete todo tasks.
"""

from uuid import UUID

from agents import function_tool
from pydantic import BaseModel, Field
from sqlalchemy import select

from database import async_session_maker
from tools import format_error_response, format_success_response


class DeleteTaskInput(BaseModel):
    """Input parameters for deleting a task."""

    user_id: str = Field(..., description="User UUID")
    task_id: str = Field(..., description="Task UUID to delete")


@function_tool
async def delete_task(params: DeleteTaskInput) -> str:
    """Permanently delete a todo task.

    This function deletes the specified task from the database.
    This operation is destructive and cannot be undone.

    Args:
        params: Parameters including user_id and task_id.

    Returns:
        JSON string confirming deletion.
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

            # Store task title for response
            task_title = task.title

            # Delete task
            await session.delete(task)
            await session.commit()

            # Return success response
            return format_success_response(
                {
                    "task_id": params.task_id,
                    "message": f"Task '{task_title}' deleted successfully",
                }
            )

    except ValueError as e:
        return format_error_response(f"Invalid ID format: {str(e)}", "INVALID_ID")
    except Exception as e:
        return format_error_response(
            f"Failed to delete task: {str(e)}", "DELETE_FAILED"
        )
