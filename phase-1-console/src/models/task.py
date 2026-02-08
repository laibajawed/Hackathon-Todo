"""Task model for todo application"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    """Represents a single todo item.

    Attributes:
        id: Auto-incrementing unique identifier
        title: Task title (required, 1-200 characters)
        description: Optional task description
        completed: Completion status (default False)
        created_at: Timestamp when task was created (auto-generated)
    """

    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate task data after initialization."""
        self._validate_title()

    def _validate_title(self) -> None:
        """Validate title meets requirements.

        Raises:
            ValueError: If title is empty, whitespace-only, or exceeds 200 characters
        """
        if not self.title or not self.title.strip():
            raise ValueError("Task title cannot be empty")
        if len(self.title) > 200:
            raise ValueError("Task title must be 200 characters or less")
