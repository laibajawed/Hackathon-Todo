"""User context-aware function tools for AI agent.

This module provides wrapper tools that automatically inject user_id from
authentication context, eliminating the need for users to provide it.

IMPORTANT: All parameters are REQUIRED (no Optional) for Groq API compatibility.
Empty strings are used as sentinel values for "not provided".
"""

from agents import function_tool

# Store user context globally (will be set per request)
_current_user_id: str | None = None


def set_user_context(user_id: str):
    """Set the current user context for tool execution."""
    global _current_user_id
    _current_user_id = user_id


def get_user_context() -> str:
    """Get the current user context."""
    if _current_user_id is None:
        raise ValueError("User context not set")
    return _current_user_id


# Context-aware wrapper tools with ALL REQUIRED PARAMETERS for Groq compatibility
@function_tool(strict_mode=False)
async def create_task(title: str, description: str = "") -> str:
    """Create a new todo task for the authenticated user.

    Args:
        title: Task title (1-200 characters, required)
        description: Task description (max 2000 characters, use empty string if none)

    Returns:
        JSON string with task creation result
    """
    from tools.create_task import create_task as original_create_task, CreateTaskInput as OriginalInput

    # Inject user_id from context
    # Convert empty string to None for optional description
    full_params = OriginalInput(
        user_id=get_user_context(),
        title=title,
        description=description if description else None
    )
    return await original_create_task(full_params)


@function_tool(strict_mode=False)
async def list_tasks(status: str = "", limit: int = 50) -> str:
    """List todo tasks for the authenticated user.

    Args:
        status: Filter by status: 'pending', 'completed', or empty string for all tasks
        limit: Maximum number of tasks to return (1-100, default 50)

    Returns:
        JSON string with list of tasks
    """
    from tools.list_tasks import list_tasks as original_list_tasks, ListTasksInput as OriginalInput

    # Inject user_id from context
    # Convert empty string to None for optional status
    full_params = OriginalInput(
        user_id=get_user_context(),
        status=status if status else None,
        limit=limit
    )
    return await original_list_tasks(full_params)


@function_tool(strict_mode=False)
async def update_task(task_id: str, title: str = "", description: str = "") -> str:
    """Update an existing todo task for the authenticated user.

    Args:
        task_id: Task ID to update (required)
        title: New task title (1-200 characters, use empty string to keep current)
        description: New task description (max 2000 characters, use empty string to keep current)

    Returns:
        JSON string with update result
    """
    from tools.update_task import update_task as original_update_task, UpdateTaskInput as OriginalInput

    # Inject user_id from context
    # Convert empty strings to None for optional fields
    full_params = OriginalInput(
        user_id=get_user_context(),
        task_id=task_id,
        title=title if title else None,
        description=description if description else None
    )
    return await original_update_task(full_params)


@function_tool(strict_mode=False)
async def toggle_task_status(task_id: str) -> str:
    """Toggle a task's completion status (pending <-> completed) for the authenticated user.

    Args:
        task_id: Task ID to toggle (required)

    Returns:
        JSON string with toggle result
    """
    from tools.toggle_task_status import toggle_task_status as original_toggle, ToggleTaskStatusInput as OriginalInput

    # Inject user_id from context
    full_params = OriginalInput(
        user_id=get_user_context(),
        task_id=task_id
    )
    return await original_toggle(full_params)


@function_tool(strict_mode=False)
async def delete_task(task_id: str) -> str:
    """Delete a todo task for the authenticated user.

    Args:
        task_id: Task ID to delete (required)

    Returns:
        JSON string with deletion result
    """
    from tools.delete_task import delete_task as original_delete_task, DeleteTaskInput as OriginalInput

    # Inject user_id from context
    full_params = OriginalInput(
        user_id=get_user_context(),
        task_id=task_id
    )
    return await original_delete_task(full_params)
