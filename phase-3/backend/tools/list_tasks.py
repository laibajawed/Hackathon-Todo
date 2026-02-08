"""List tasks function tool for OpenAI Agents SDK.

This tool enables the AI agent to retrieve and list user's todo tasks.
"""

from typing import Optional

from agents import function_tool
from pydantic import BaseModel, Field
from sqlalchemy import select
from uuid import UUID

from database import async_session_maker
from tools import format_error_response, format_success_response


class ListTasksInput(BaseModel):
    """Input parameters for listing tasks."""

    user_id: str = Field(..., description="User UUID")
    status: Optional[str] = Field(
        None, description="Filter by status: 'pending' or 'completed'"
    )
    limit: int = Field(50, ge=1, le=100, description="Maximum number of tasks to return")


@function_tool
async def list_tasks(params: ListTasksInput) -> str:
    """List todo tasks for the user with optional filtering.

    This function retrieves tasks for the specified user, optionally filtered by status.
    Results are limited to prevent overwhelming responses.

    Args:
        params: Task listing parameters including user_id, optional status filter, and limit.

    Returns:
        JSON string with list of tasks and total count.
    """
    try:
        # Validate status filter
        if params.status and params.status not in ["pending", "completed"]:
            return format_error_response(
                "Status must be 'pending' or 'completed'", "INVALID_STATUS"
            )

        # Create database session
        async with async_session_maker() as session:
            # Import Task model
            from models import Task

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

            # Format tasks
            formatted_tasks = [
                {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "created_at": task.created_at.isoformat() if hasattr(task, "created_at") else None,
                }
                for task in tasks
            ]

            # Return success response
            return format_success_response(
                {
                    "tasks": formatted_tasks,
                    "total": len(formatted_tasks),
                    "filter": params.status or "all",
                }
            )

    except ValueError as e:
        return format_error_response(f"Invalid user ID format: {str(e)}", "INVALID_USER_ID")
    except Exception as e:
        return format_error_response(
            f"Failed to list tasks: {str(e)}", "TASK_LIST_FAILED"
        )
