"""Tool wrapper to inject user context into function tools.

This module provides utilities to bind authenticated user context to function tools,
eliminating the need for users to provide their user_id in natural language.
"""

from functools import partial
from typing import Any, Callable, List
from agents import function_tool
from pydantic import BaseModel, Field


def create_user_bound_tools(user_id: str, tools: List[Callable]) -> List[Callable]:
    """Create versions of tools with user_id pre-bound from JWT context.
    
    Args:
        user_id: Authenticated user's ID from JWT token
        tools: List of function tools that require user_id parameter
        
    Returns:
        List of wrapped tools with user_id automatically injected
    """
    bound_tools = []
    
    for tool in tools:
        # Create a wrapper that injects user_id
        async def wrapped_tool(params: Any, _user_id: str = user_id, _original_tool: Callable = tool) -> str:
            # Inject user_id into params if it has that field
            if hasattr(params, 'user_id'):
                params.user_id = _user_id
            return await _original_tool(params)
        
        # Preserve tool metadata
        wrapped_tool.__name__ = tool.__name__
        wrapped_tool.__doc__ = tool.__doc__
        
        bound_tools.append(wrapped_tool)
    
    return bound_tools
