"""TodoManager - Business logic for task management"""

from typing import List, Dict, Optional
from src.models.task import Task


class TodoManager:
    """Manages in-memory task storage and CRUD operations."""

    def __init__(self) -> None:
        """Initialize TodoManager with empty in-memory storage."""
        self._tasks: Dict[int, Task] = {}

    def add_task(self, title: str, description: Optional[str] = None) -> Task:
        """Create a new task with provided title and optional description.

        Args:
            title: Task title, must be 1-200 characters
            description: Task description, defaults to None

        Returns:
            Task: The newly created task object with auto-assigned ID

        Raises:
            ValueError: If title is empty, whitespace-only, or exceeds 200 characters
        """
        # Validate title
        title = title.strip()
        if not title:
            raise ValueError("Task title cannot be empty")
        if len(title) > 200:
            raise ValueError("Task title must be 200 characters or less")

        # Generate next ID
        next_id = max(self._tasks.keys(), default=0) + 1

        # Create task
        task = Task(
            id=next_id,
            title=title,
            description=description,
            completed=False
        )

        # Store task
        self._tasks[next_id] = task

        return task

    def list_tasks(self) -> List[Task]:
        """Return all tasks currently stored in memory.

        Returns:
            List[Task]: List of all task objects, ordered by ID

        Side Effects:
            None (read-only operation)
        """
        return [self._tasks[id] for id in sorted(self._tasks.keys())]

    def update_task(self, task_id: int, title: Optional[str] = None,
                description: Optional[str] = None) -> Task:
        """Update an existing task's title and/or description.

        Args:
            task_id: ID of task to update
            title: New title (unchanged if None)
            description: New description (unchanged if None)

        Returns:
            Task: The updated task object

        Raises:
            ValueError: If task_id not found
            ValueError: If title is invalid when provided
        """
        if task_id not in self._tasks:
            raise ValueError(f"Task with ID {task_id} not found")

        task = self._tasks[task_id]

        # Update title if provided
        if title is not None:
            title = title.strip()
            if not title:
                raise ValueError("Task title cannot be empty")
            if len(title) > 200:
                raise ValueError("Task title must be 200 characters or less")
            task.title = title

        # Update description (can be None to clear)
        if description is not None:
            task.description = description if description else None

        return task

    def delete_task(self, task_id: int) -> bool:
        """Remove a task from storage by its ID.

        Args:
            task_id: ID of task to delete

        Returns:
            bool: True if task was deleted, False if not found

        Side Effects:
            Removes task from storage dictionary if found
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def toggle_complete(self, task_id: int) -> Task:
        """Toggle completion status of a task.

        Args:
            task_id: ID of task to toggle

        Returns:
            Task: The updated task with toggled completed status

        Raises:
            ValueError: If task_id not found
        """
        if task_id not in self._tasks:
            raise ValueError(f"Task with ID {task_id} not found")

        task = self._tasks[task_id]
        task.completed = not task.completed

        return task
