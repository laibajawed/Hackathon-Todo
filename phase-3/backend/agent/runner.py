"""Agent runner using OpenAI Agents SDK with MCP tools and Groq.

This module configures and runs the AI agent for natural language
task management using MCP (Model Context Protocol) tools.
"""

import os
import sys
from typing import Any, Dict, List, Optional

from agents import Agent, Runner
from agents.extensions.models.litellm_model import LitellmModel
from agents.mcp import MCPServerStdio

# Agent configuration - Groq only
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is required")

AI_MODEL = "groq/openai/gpt-oss-20b"  # LiteLLM format: groq/ prefix + Groq model name
AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "1000"))
AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.7"))

print("✓ Using Groq with groq/openai/gpt-oss-20b", file=sys.stderr)

# Agent instructions for task management
AGENT_INSTRUCTIONS = """You are a helpful AI assistant that helps users manage their todo tasks through natural language conversation.

Your capabilities:
- Create new tasks when users describe things they need to do
- List tasks when users ask what's on their list
- Mark tasks as complete when users indicate they've finished something
- Update task details when users want to modify existing tasks
- Delete tasks when users want to remove them

CRITICAL - Task ID Handling:
- Tasks have UUID IDs (e.g., "a1b2c3d4-e5f6-7890-abcd-ef1234567890")
- When you call list_tasks, parse the JSON response to extract task IDs
- Remember the task IDs from the most recent list_tasks call
- When users refer to tasks by number (e.g., "1", "the first one", "task 2"), map that to the actual UUID from your list
- Example: If list_tasks returns [{"id": "abc-123", "title": "Buy groceries"}], and user says "mark 1 as complete", use task_id="abc-123"

Guidelines:
1. Always call list_tasks FIRST before updating/toggling/deleting tasks to get current task IDs
2. Parse JSON responses from tools to extract task IDs and other data
3. When listing tasks, present them as: "1. Buy groceries (ID: abc-123...)" or just "1. Buy groceries"
4. Map user references (numbers, descriptions) to actual UUIDs from your most recent list_tasks call
5. Always confirm actions clearly ("I've added 'buy groceries' to your list")
6. For ambiguous commands, ask clarifying questions
7. Be conversational and friendly
8. Always use the provided MCP tools - never pretend to complete actions

Remember: You MUST call list_tasks before any update/toggle/delete operation to get the correct task IDs.
"""


def get_mcp_server_config(user_id: str, database_url: str) -> dict:
    """Get MCP server configuration for subprocess creation.

    Args:
        user_id: UUID of the authenticated user
        database_url: PostgreSQL connection string

    Returns:
        Dictionary with command, args, and env for MCPServerStdio
    """
    import pathlib

    backend_dir = pathlib.Path(__file__).parent.parent
    mcp_server_path = backend_dir / "mcp_server" / "server.py"

    subprocess_env = os.environ.copy()
    subprocess_env.update({
        "USER_ID": user_id,
        "DATABASE_URL": database_url,
        "PYTHONPATH": str(backend_dir),
    })

    return {
        "command": sys.executable,
        "args": [str(mcp_server_path)],
        "env": subprocess_env
    }




async def run_agent_with_mcp(
    user_id: str,
    database_url: str,
    user_message: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """Run the agent with MCP tools and user message.

    This function:
    1. Spawns an MCP server subprocess with user-specific context
    2. Creates an agent with the MCP server
    3. Runs the agent with the user's message

    Args:
        user_id: UUID of the authenticated user
        database_url: PostgreSQL connection string
        user_message: User's message text
        conversation_history: Optional list of previous messages for context
            Format: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]

    Returns:
        Dictionary with agent response and metadata:
        {
            "response": str,  # Agent's final response
            "tool_calls": List[Dict],  # Tools that were invoked
            "tokens_used": int,  # Estimated token count
            "error": bool  # Whether an error occurred
        }
    """
    import logging
    from agents import ModelSettings

    logger = logging.getLogger(__name__)

    try:
        # Get MCP server configuration with user context
        server_config = get_mcp_server_config(user_id, database_url)

        # Use OpenAI Agents SDK's native MCP integration
        async with MCPServerStdio(
            name="Todo MCP Server",
            params=server_config,
            client_session_timeout_seconds=30.0,  # Increase timeout from default 5s
        ) as mcp_server:
            logger.info(f"MCP server initialized for user {user_id}")

            # Create agent with MCP server
            agent = Agent(
                name="Todo Assistant",
                instructions=AGENT_INSTRUCTIONS,
                model=LitellmModel(
                    model=AI_MODEL,
                    api_key=GROQ_API_KEY,
                ),
                model_settings=ModelSettings(
                    kwargs={
                        "max_tokens": AI_MAX_TOKENS,
                        "temperature": AI_TEMPERATURE,
                    }
                ),
                mcp_servers=[mcp_server],
            )
            logger.info("Agent created with MCP server")

            # Build messages list with conversation history
            messages = []
            if conversation_history:
                messages.extend(conversation_history)

            # Add current user message
            messages.append({"role": "user", "content": user_message})

            # Run agent with OpenAI Agents SDK
            logger.info("Running agent...")
            result = await Runner.run(agent, messages)
            logger.info("Agent execution completed")

            # Extract response and metadata
            return {
                "response": result.final_output,
                "tool_calls": result.tool_calls if hasattr(result, "tool_calls") else [],
                "tokens_used": result.tokens_used if hasattr(result, "tokens_used") else 0,
                "error": False,
            }

    except Exception as e:
        # Log error and return user-friendly message
        logger.error(f"Agent execution error for user {user_id}: {e}", exc_info=True)

        return {
            "response": "I'm having trouble connecting right now. Please try again in a moment.",
            "tool_calls": [],
            "tokens_used": 0,
            "error": True,
            "error_message": str(e),
        }


