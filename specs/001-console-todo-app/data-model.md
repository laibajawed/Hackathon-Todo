# Data Model: Phase I Console Todo Application

**Feature**: 001-console-todo-app
**Phase**: Phase I (In-Memory CLI)
**Date**: 2026-01-06

## Entity: Task

### Description

Represents a single todo item that a user creates, tracks, and manages.

### Attributes

| Attribute | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| `id` | `int` | Yes | Auto-incrementing, unique | Unique identifier for the task |
| `title` | `str` | Yes | 1-200 characters | The task title/name |
| `description` | `str` | No | Any length, optional | Additional details about the task |
| `completed` | `bool` | Yes | Default: `False` | Completion status of the task |
| `created_at` | `datetime` | Yes | Auto-generated | Timestamp when task was created |

### Validation Rules

1. **Title Validation** (FR-009):
   - Must not be empty or whitespace-only
   - Maximum length: 200 characters
   - Trim leading/trailing whitespace

2. **Description** (FR-002):
   - Optional field (can be `None` or empty string)
   - No length restrictions
   - Can contain any characters

3. **ID Generation** (FR-003):
   - Auto-incrementing integer
   - Starts at 1 for first task
   - Increments by 1 for each new task
   - Never reuses deleted task IDs

4. **Timestamp**:
   - Automatically set on creation
   - Use ISO 8601 format for display
   - Stored as Python `datetime` object

### State Transitions

```
[Task Created]
    |
    v
[Pending (completed=False)]  <--->  [Complete (completed=True)]
    |
    v
[Task Deleted]
```

**Transition Rules**:
- Tasks start in `Pending` state (`completed=False`)
- Only valid transition is `Pending` ↔ `Complete` (toggle)
- Once deleted, task is removed from storage

### Relationships

No relationships in Phase I (single-user, in-memory storage).

Evolution Note: In later phases with database layer and multi-user support, tasks will have relationships to users and potentially categories/tags.

### Implementation Notes

**Dataclass Approach** (per plan):
```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Task:
    id: int
    title: str
    description: str
    completed: bool = False
    created_at: datetime = datetime.utcnow()
```

**Type Hints**:
- Use Python type hints for all attributes
- `Optional[str]` for description to indicate it may be `None`
- Return types for all methods

**Error Handling**:
- Raise `ValueError` for invalid title (empty or >200 chars)
- No exceptions for optional description field

### Storage Implementation

**In-Memory Storage** (Phase I):
- Use Python `list` or `dict` to store Task objects
- Dictionary with ID as key recommended for O(1) lookup
```python
tasks: Dict[int, Task] = {}
```

**CRUD Operations** (via TodoManager):
- `add_task(title, description)` → Create new Task with next ID
- `list_tasks()` → Return list of all Tasks
- `update_task(id, title, description)` → Find by ID, update fields
- `delete_task(id)` → Remove from dictionary
- `toggle_complete(id)` → Toggle `completed` boolean

### Evolution Path

**Phase I (Current)**:
- In-memory storage: `Dict[int, Task]`
- Single-user, no relationships
- Dataclass representation

**Phase II+ (Future)**:
- PostgreSQL database with SQLModel ORM
- User relationships (multi-tenancy)
- Additional fields: priority, due_date, tags
- Database constraints and indexes
