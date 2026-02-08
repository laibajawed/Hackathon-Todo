"""MCP server for todo task management tools.

This server exposes 5 tools for AI agents to manage todo tasks:
- list_tasks: List tasks with optional filtering
- create_task: Create new tasks
- toggle_task_status: Toggle task status between pending/completed
- update_task: Update task title and/or description
- delete_task: Permanently delete tasks

The server runs as a standalone HTTP service using streamable-http transport.
User context (user_id) is passed as a parameter to each tool for proper isolation.
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional
from uuid import UUID

# Add parent directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Import database and model utilities
# Use lazy initialization to avoid import-time database connection
from database import get_async_session_maker
from models import Task
from tools import sanitize_input, format_error_response, format_success_response

# Session maker will be initialized on first use
_async_session_maker = None

def get_session_maker():
    """Get or create the async session maker."""
    global _async_session_maker
    if _async_session_maker is None:
        _async_session_maker = get_async_session_maker()
    return _async_session_maker

# Import FastMCP
from mcp.server.fastmcp import FastMCP

# Create FastMCP server instance
mcp = FastMCP("todo-tools")


def get_database_url():
    """Get DATABASE_URL from environment, with validation."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is required")
    return database_url


@mcp.tool(description="List todo tasks with optional filtering by status")
async def list_tasks(
    user_id: str,
    status: Optional[str] = None,
    limit: int = 50
) -> str:
    """List todo tasks for the user with optional filtering.

    Args:
        user_id: UUID of the user (required for user isolation)
        status: Optional filter by status ('pending' or 'completed')
        limit: Maximum number of tasks to return (1-100, default 50)

    Returns:
        JSON string with list of tasks and total count
    """
    try:
        # Validate user_id format
        try:
            UUID(user_id)
        except ValueError:
            return format_error_response(
                "Invalid user_id format. Must be a valid UUID.", "INVALID_USER_ID"
            )

        # Validate status filter
        if status and status not in ["pending", "completed"]:
            return format_error_response(
                "Status must be 'pending' or 'completed'", "INVALID_STATUS"
            )

        # Validate limit
        if limit < 1 or limit > 100:
            return format_error_response(
                "Limit must be between 1 and 100", "INVALID_LIMIT"
            )

        # Create database session
        async with get_session_maker()() as session:
            from sqlalchemy import select

            # Build query with user isolation
            statement = select(Task).where(Task.user_id == UUID(user_id))

            # Apply status filter if provided
            if status:
                statement = statement.where(Task.status == status)

            # Apply limit
            statement = statement.limit(limit)

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
                    "filter": status or "all",
                }
            )

    except ValueError as e:
        return format_error_response(f"Invalid user ID format: {str(e)}", "INVALID_USER_ID")
    except Exception as e:
        return format_error_response(
            f"Failed to list tasks: {str(e)}", "TASK_LIST_FAILED"
        )


@mcp.tool(description="Create a new todo task")
async def create_task(
    user_id: str,
    title: str,
    description: Optional[str] = None
) -> str:
    """Create a new todo task for the user.

    Args:
        user_id: UUID of the user (required for user isolation)
        title: Task title (1-200 characters, required)
        description: Optional task description (max 2000 characters)

    Returns:
        JSON string with created task details
    """
    try:
        # Validate user_id format
        try:
            UUID(user_id)
        except ValueError:
            return format_error_response(
                "Invalid user_id format. Must be a valid UUID.", "INVALID_USER_ID"
            )

        # Sanitize inputs to prevent XSS
        title_clean = sanitize_input(title)
        description_clean = sanitize_input(description) if description else None

        # Validate title length
        if len(title_clean) < 1 or len(title_clean) > 200:
            return format_error_response(
                "Task title must be between 1 and 200 characters", "INVALID_INPUT"
            )

        # Validate description length
        if description_clean and len(description_clean) > 2000:
            return format_error_response(
                "Task description must be 2000 characters or less", "INVALID_INPUT"
            )

        # Create database session
        async with get_session_maker()() as session:
            # Create new task with user isolation
            task = Task(
                user_id=UUID(user_id),
                title=title_clean,
                description=description_clean,
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


@mcp.tool(description="Toggle task status between pending and completed")
async def toggle_task_status(user_id: str, task_id: str) -> str:
    """Toggle a task's status between pending and completed.

    Args:
        user_id: UUID of the user (required for user isolation)
        task_id: UUID of the task to toggle

    Returns:
        JSON string with updated task status
    """
    try:
        # Validate user_id format
        try:
            UUID(user_id)
        except ValueError:
            return format_error_response(
                "Invalid user_id format. Must be a valid UUID.", "INVALID_USER_ID"
            )

        # Create database session
        async with get_session_maker()() as session:
            from sqlalchemy import select

            # Find task with ownership verification
            statement = select(Task).where(
                Task.id == UUID(task_id),
                Task.user_id == UUID(user_id),
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


@mcp.tool(description="Update task title and/or description")
async def update_task(
    user_id: str,
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> str:
    """Update a task's title and/or description.

    Args:
        user_id: UUID of the user (required for user isolation)
        task_id: UUID of the task to update
        title: New task title (1-200 characters, optional)
        description: New task description (max 2000 characters, optional)

    Returns:
        JSON string with updated task details
    """
    try:
        # Validate user_id format
        try:
            UUID(user_id)
        except ValueError:
            return format_error_response(
                "Invalid user_id format. Must be a valid UUID.", "INVALID_USER_ID"
            )

        # Validate that at least one field is provided
        if not title and description is None:
            return format_error_response(
                "At least one field (title or description) must be provided",
                "NO_FIELDS_PROVIDED",
            )

        # Sanitize inputs
        title_clean = sanitize_input(title) if title else None
        description_clean = (
            sanitize_input(description) if description else None
        )

        # Validate lengths
        if title_clean and (len(title_clean) < 1 or len(title_clean) > 200):
            return format_error_response(
                "Task title must be between 1 and 200 characters", "INVALID_INPUT"
            )

        if description_clean and len(description_clean) > 2000:
            return format_error_response(
                "Task description must be 2000 characters or less", "INVALID_INPUT"
            )

        # Create database session
        async with get_session_maker()() as session:
            from sqlalchemy import select

            # Find task with ownership verification
            statement = select(Task).where(
                Task.id == UUID(task_id),
                Task.user_id == UUID(user_id),
            )
            result = await session.execute(statement)
            task = result.scalar_one_or_none()

            if not task:
                return format_error_response(
                    "Task not found or you don't have permission to access it",
                    "TASK_NOT_FOUND",
                )

            # Update fields
            if title_clean:
                task.title = title_clean
            if description_clean is not None:
                task.description = description_clean

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


@mcp.tool(description="Permanently delete a task")
async def delete_task(user_id: str, task_id: str) -> str:
    """Permanently delete a todo task.

    Args:
        user_id: UUID of the user (required for user isolation)
        task_id: UUID of the task to delete

    Returns:
        JSON string confirming deletion
    """
    try:
        # Validate user_id format
        try:
            UUID(user_id)
        except ValueError:
            return format_error_response(
                "Invalid user_id format. Must be a valid UUID.", "INVALID_USER_ID"
            )

        # Create database session
        async with get_session_maker()() as session:
            from sqlalchemy import select

            # Find task with ownership verification
            statement = select(Task).where(
                Task.id == UUID(task_id),
                Task.user_id == UUID(user_id),
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
                    "task_id": task_id,
                    "message": f"Task '{task_title}' deleted successfully",
                }
            )

    except ValueError as e:
        return format_error_response(f"Invalid ID format: {str(e)}", "INVALID_ID")
    except Exception as e:
        return format_error_response(
            f"Failed to delete task: {str(e)}", "DELETE_FAILED"
        )


def main():
    """Run the MCP server with stdio transport."""
    import logging

    # Configure logging to stderr (not stdout, which is used for MCP communication)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr
    )

    logger = logging.getLogger(__name__)
    logger.info("Starting MCP server with stdio transport")

    # Validate DATABASE_URL is available
    try:
        database_url = get_database_url()
        logger.info(f"Database URL configured: {bool(database_url)}")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)

    logger.info(f"User ID from environment: {os.getenv('USER_ID', 'not set')}")

    try:
        # Use stdio transport for subprocess communication
        # This allows the agent runner to spawn the server as a subprocess
        # and communicate via stdin/stdout
        mcp.run(transport="stdio")
    except Exception as e:
        logger.error(f"MCP server failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
