"""MCP server for todo task management tools using official SDK.

Uses lazy imports to avoid blocking during subprocess startup.
All database/model imports happen inside async functions.
"""

import sys
print("=== MCP SERVER STARTING ===", file=sys.stderr, flush=True)

import json
import logging
import os
from pathlib import Path
from typing import Any, Optional

# Configure logging to stderr only
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Add parent directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Import MCP SDK (lightweight, no database dependencies)
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

print("=== MCP SDK IMPORTED ===", file=sys.stderr, flush=True)

# Create MCP server instance
server = Server("todo-tools")

# Global session maker (created lazily)
_async_session_maker = None


def get_database_url():
    """Get DATABASE_URL from environment."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is required")
    return database_url


def get_user_id():
    """Get USER_ID from environment."""
    user_id = os.getenv("USER_ID")
    if not user_id:
        raise ValueError("USER_ID environment variable is required")
    return user_id


def get_session_maker():
    """Get or create session maker with lazy imports."""
    global _async_session_maker
    if _async_session_maker is None:
        # Lazy import - only import when first needed
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
        
        database_url = get_database_url()
        engine = create_async_engine(
            database_url,
            echo=False,
            future=True,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )
        _async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _async_session_maker


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="list_tasks",
            description="List todo tasks with optional filtering by status",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["pending", "completed"], "description": "Filter by task status"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 50, "description": "Maximum number of tasks to return"}
                },
                "required": []
            }
        ),
        Tool(
            name="create_task",
            description="Create a new todo task",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "minLength": 1, "maxLength": 200, "description": "Task title"},
                    "description": {"type": "string", "maxLength": 1000, "description": "Optional task description"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high"], "default": "medium", "description": "Task priority level"},
                    "tag": {"type": "string", "maxLength": 50, "description": "Optional task tag"}
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="toggle_task_status",
            description="Toggle task status between pending and completed",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "UUID of the task to toggle"}
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="update_task",
            description="Update task title, description, priority, and/or tag",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "UUID of the task to update"},
                    "title": {"type": "string", "minLength": 1, "maxLength": 200, "description": "New task title"},
                    "description": {"type": "string", "maxLength": 1000, "description": "New task description"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "New task priority level"},
                    "tag": {"type": "string", "maxLength": 50, "description": "New task tag"}
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="delete_task",
            description="Permanently delete a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "UUID of the task to delete"}
                },
                "required": ["task_id"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls with lazy imports."""
    logger.info(f"Tool called: {name}")
    
    # Lazy import tools module
    from tools import format_error_response, format_success_response
    
    try:
        if name == "list_tasks":
            result = await handle_list_tasks(**arguments)
        elif name == "create_task":
            result = await handle_create_task(**arguments)
        elif name == "toggle_task_status":
            result = await handle_toggle_task_status(**arguments)
        elif name == "update_task":
            result = await handle_update_task(**arguments)
        elif name == "delete_task":
            result = await handle_delete_task(**arguments)
        else:
            result = format_error_response(f"Unknown tool: {name}", "UNKNOWN_TOOL")
        
        return [TextContent(type="text", text=result)]
    
    except Exception as e:
        logger.error(f"Tool error: {e}", exc_info=True)
        from tools import format_error_response
        return [TextContent(type="text", text=format_error_response(str(e), "TOOL_ERROR"))]


async def handle_list_tasks(status: Optional[str] = None, limit: int = 50) -> str:
    """List tasks with lazy imports."""
    # Lazy imports
    from uuid import UUID
    from sqlalchemy import select
    from models import Task
    from tools import format_error_response, format_success_response

    try:
        user_id = get_user_id()
        UUID(user_id)

        async with get_session_maker()() as session:
            statement = select(Task).where(Task.user_id == UUID(user_id))
            if status:
                statement = statement.where(Task.status == status)
            statement = statement.order_by(Task.created_at.desc()).limit(limit)

            result = await session.execute(statement)
            tasks = result.scalars().all()

            task_list = [
                {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "priority": task.priority,
                    "tag": task.tag,
                    "status": task.status,
                    "created_at": task.created_at.isoformat(),
                }
                for task in tasks
            ]

            return format_success_response({
                "tasks": task_list,
                "total": len(task_list),
                "filter": status or "all"
            })

    except Exception as e:
        logger.error(f"List tasks error: {e}")
        return format_error_response(str(e), "LIST_FAILED")


async def handle_create_task(title: str, description: Optional[str] = None, priority: str = "medium", tag: Optional[str] = None) -> str:
    """Create task with lazy imports."""
    from uuid import UUID
    from datetime import datetime
    from models import Task, TaskPriority
    from tools import sanitize_input, format_error_response, format_success_response

    try:
        user_id = get_user_id()
        UUID(user_id)
        title_clean = sanitize_input(title)
        description_clean = sanitize_input(description) if description else None
        tag_clean = sanitize_input(tag) if tag else None

        async with get_session_maker()() as session:
            task = Task(
                user_id=UUID(user_id),
                title=title_clean,
                description=description_clean,
                priority=TaskPriority(priority),
                tag=tag_clean,
                status="pending",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(task)
            await session.commit()
            await session.refresh(task)

            return format_success_response({
                "task": {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "priority": task.priority,
                    "tag": task.tag,
                    "status": task.status,
                },
                "message": f"Task '{task.title}' created successfully"
            })

    except Exception as e:
        logger.error(f"Create task error: {e}")
        return format_error_response(str(e), "CREATE_FAILED")


async def handle_toggle_task_status(task_id: str) -> str:
    """Toggle task status with lazy imports."""
    from uuid import UUID
    from sqlalchemy import select
    from models import Task
    from tools import format_error_response, format_success_response

    try:
        user_id = get_user_id()
        UUID(user_id)

        async with get_session_maker()() as session:
            statement = select(Task).where(
                Task.id == UUID(task_id),
                Task.user_id == UUID(user_id)
            )
            result = await session.execute(statement)
            task = result.scalar_one_or_none()

            if not task:
                return format_error_response("Task not found", "TASK_NOT_FOUND")

            old_status = task.status
            task.status = "completed" if task.status == "pending" else "pending"

            session.add(task)
            await session.commit()
            await session.refresh(task)

            return format_success_response({
                "task": {
                    "id": str(task.id),
                    "title": task.title,
                    "status": task.status
                },
                "message": f"Task '{task.title}' marked as {task.status}",
                "previous_status": old_status
            })

    except Exception as e:
        logger.error(f"Toggle error: {e}")
        return format_error_response(str(e), "TOGGLE_FAILED")


async def handle_update_task(task_id: str, title: Optional[str] = None, description: Optional[str] = None, priority: Optional[str] = None, tag: Optional[str] = None) -> str:
    """Update task with lazy imports."""
    from uuid import UUID
    from sqlalchemy import select
    from models import Task, TaskPriority
    from tools import sanitize_input, format_error_response, format_success_response

    try:
        user_id = get_user_id()
        UUID(user_id)

        async with get_session_maker()() as session:
            statement = select(Task).where(
                Task.id == UUID(task_id),
                Task.user_id == UUID(user_id)
            )
            result = await session.execute(statement)
            task = result.scalar_one_or_none()

            if not task:
                return format_error_response("Task not found", "TASK_NOT_FOUND")

            if title:
                task.title = sanitize_input(title)
            if description is not None:
                task.description = sanitize_input(description)
            if priority:
                task.priority = TaskPriority(priority)
            if tag is not None:
                task.tag = sanitize_input(tag) if tag else None

            session.add(task)
            await session.commit()
            await session.refresh(task)

            return format_success_response({
                "task": {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "priority": task.priority,
                    "tag": task.tag,
                    "status": task.status
                },
                "message": f"Task '{task.title}' updated successfully"
            })

    except Exception as e:
        logger.error(f"Update error: {e}")
        return format_error_response(str(e), "UPDATE_FAILED")


async def handle_delete_task(task_id: str) -> str:
    """Delete task with lazy imports."""
    from uuid import UUID
    from sqlalchemy import select
    from models import Task
    from tools import format_error_response, format_success_response

    try:
        user_id = get_user_id()
        UUID(user_id)

        async with get_session_maker()() as session:
            statement = select(Task).where(
                Task.id == UUID(task_id),
                Task.user_id == UUID(user_id)
            )
            result = await session.execute(statement)
            task = result.scalar_one_or_none()

            if not task:
                return format_error_response("Task not found", "TASK_NOT_FOUND")

            task_title = task.title
            await session.delete(task)
            await session.commit()

            return format_success_response({
                "task_id": task_id,
                "message": f"Task '{task_title}' deleted successfully"
            })

    except Exception as e:
        logger.error(f"Delete error: {e}")
        return format_error_response(str(e), "DELETE_FAILED")


async def main():
    """Run the MCP server."""
    logger.info("Starting MCP server with stdio transport")
    print("=== STARTING STDIO SERVER ===", file=sys.stderr, flush=True)
    
    try:
        database_url = get_database_url()
        logger.info(f"Database URL configured: {bool(database_url)}")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Server running on stdio transport")
            print("=== SERVER READY ===", file=sys.stderr, flush=True)
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"Server failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    import asyncio
    print("=== RUNNING MAIN ===", file=sys.stderr, flush=True)
    asyncio.run(main())
