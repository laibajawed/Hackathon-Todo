"""
Task routes for CRUD operations on tasks.
Provides endpoints for creating, reading, updating, and deleting tasks.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_session
from models import Task, TaskStatus
from auth.dependencies import get_current_user_id
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List
import html


router = APIRouter()


def sanitize_input(text: str) -> str:
    """Escape HTML entities to prevent XSS attacks."""
    return html.escape(text)


# Pydantic schemas for task operations
class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)


class TaskResponse(BaseModel):
    """Schema for task response."""
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    status: Optional[TaskStatus] = Query(default=None, description="Filter by task status"),
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """
    Get all tasks for the authenticated user.

    Optionally filter by status (pending or completed).

    Args:
        status: Optional status filter (pending or completed)
        current_user_id: Authenticated user's ID from JWT
        session: Database session

    Returns:
        List of tasks belonging to the user
    """
    # Build query with user_id filter
    statement = select(Task).where(Task.user_id == current_user_id)

    # Add status filter if provided
    if status:
        statement = statement.where(Task.status == status)

    # Order by created_at descending (newest first)
    statement = statement.order_by(Task.created_at.desc())

    result = await session.execute(statement)
    tasks = result.scalars().all()

    return tasks


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """
    Create a new task for the authenticated user.

    Args:
        task_data: Task creation data (title and optional description)
        current_user_id: Authenticated user's ID from JWT
        session: Database session

    Returns:
        Created task

    Raises:
        HTTPException: If title is empty (400 Bad Request)
    """
    # Validate title is not empty
    if not task_data.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task title cannot be empty"
        )

    # Sanitize inputs to prevent XSS
    sanitized_title = sanitize_input(task_data.title.strip())
    sanitized_description = sanitize_input(task_data.description.strip()) if task_data.description else None

    # Create new task
    new_task = Task(
        user_id=current_user_id,
        title=sanitized_title,
        description=sanitized_description,
        status=TaskStatus.PENDING
    )

    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)

    return new_task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """
    Update a task's title and/or description.

    Args:
        task_id: Task ID to update
        task_data: Task update data (title and/or description)
        current_user_id: Authenticated user's ID from JWT
        session: Database session

    Returns:
        Updated task

    Raises:
        HTTPException: If task not found or doesn't belong to user (404)
        HTTPException: If title is empty (400)
    """
    # Find task and verify ownership
    statement = select(Task).where(Task.id == task_id, Task.user_id == current_user_id)
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update title if provided
    if task_data.title is not None:
        if not task_data.title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task title cannot be empty"
            )
        task.title = sanitize_input(task_data.title.strip())

    # Update description if provided
    if task_data.description is not None:
        task.description = sanitize_input(task_data.description.strip()) if task_data.description.strip() else None

    # Update timestamp
    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return task


@router.patch("/{task_id}/toggle", response_model=TaskResponse)
async def toggle_task_status(
    task_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """
    Toggle a task's completion status between pending and completed.

    Args:
        task_id: Task ID to toggle
        current_user_id: Authenticated user's ID from JWT
        session: Database session

    Returns:
        Updated task with toggled status

    Raises:
        HTTPException: If task not found or doesn't belong to user (404)
    """
    # Find task and verify ownership
    statement = select(Task).where(Task.id == task_id, Task.user_id == current_user_id)
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Toggle status
    task.status = TaskStatus.COMPLETED if task.status == TaskStatus.PENDING else TaskStatus.PENDING
    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """
    Delete a task.

    Args:
        task_id: Task ID to delete
        current_user_id: Authenticated user's ID from JWT
        session: Database session

    Returns:
        No content (204)

    Raises:
        HTTPException: If task not found or doesn't belong to user (404)
    """
    # Find task and verify ownership
    statement = select(Task).where(Task.id == task_id, Task.user_id == current_user_id)
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    await session.delete(task)
    await session.commit()

    return None
