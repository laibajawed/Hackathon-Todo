"""Tool utilities and base functions for OpenAI Agents SDK function tools.

This module provides common utilities for all function tools including
user ownership verification, error handling, and tool exports.
"""

import html
from typing import Any, Dict


def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS attacks.

    Args:
        text: Raw user input string

    Returns:
        HTML-escaped string safe for storage and display
    """
    return html.escape(text)


def format_error_response(error_message: str, error_code: str = "ERROR") -> str:
    """Format an error response as JSON string.

    Args:
        error_message: Human-readable error message
        error_code: Error code for programmatic handling

    Returns:
        JSON string with error details
    """
    import json

    return json.dumps({"success": False, "error": error_message, "code": error_code})


def format_success_response(data: Dict[str, Any]) -> str:
    """Format a success response as JSON string.

    Args:
        data: Response data dictionary

    Returns:
        JSON string with success flag and data
    """
    import json

    return json.dumps({"success": True, **data})


# Import all function tools
from tools.create_task import create_task
from tools.delete_task import delete_task
from tools.list_tasks import list_tasks
from tools.toggle_task_status import toggle_task_status
from tools.update_task import update_task

# Tool exports - these will be registered with the agent
__all__ = [
    "sanitize_input",
    "format_error_response",
    "format_success_response",
    "create_task",
    "delete_task",
    "list_tasks",
    "toggle_task_status",
    "update_task",
]
