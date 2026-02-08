# TodoManager Interface Contract

**Component**: TodoManager
**Phase**: Phase I (In-Memory CLI)
**Date**: 2026-01-06

## Purpose

Defines the contract between the CLIHandler (user interface) and TodoManager (business logic) for all task management operations. This interface abstracts storage implementation and provides type-safe, validated operations.

## Class: TodoManager

### Constructor

```python
def __init__(self) -> None
```

**Description**: Initializes the TodoManager with empty in-memory storage.

**Returns**: None

**Side Effects**: Creates empty storage dictionary `self._tasks: Dict[int, Task]`

---

## Methods

### add_task

```python
def add_task(self, title: str, description: Optional[str] = None) -> Task
```

**Description**: Creates a new task with the provided title and optional description.

**Parameters**:
- `title` (str, required): Task title, must be 1-200 characters
- `description` (Optional[str], optional): Task description, defaults to None

**Returns**: `Task` - The newly created task object with auto-assigned ID

**Raises**:
- `ValueError`: If title is empty, whitespace-only, or exceeds 200 characters

**Side Effects**:
- Assigns incremental ID to task (starts at 1)
- Stores task in in-memory dictionary
- Sets `created_at` to current timestamp
- Sets `completed` to False

**Implementation Notes**:
- Title validation: `title.strip() must not be empty` and `len(title) <= 200`
- ID generation: `max(existing_ids) + 1` or 1 if first task
- Thread-safety: Not required for Phase I (single-user CLI)

---

### list_tasks

```python
def list_tasks(self) -> List[Task]
```

**Description**: Returns all tasks currently stored in memory.

**Parameters**: None

**Returns**: `List[Task]` - List of all task objects, ordered by ID

**Raises**: None

**Side Effects**: None (read-only operation)

**Edge Cases** (FR-013):
- Empty task list: Returns empty list `[]`

---

### update_task

```python
def update_task(self, task_id: int, title: Optional[str] = None,
                description: Optional[str] = None) -> Task
```

**Description**: Updates an existing task's title and/or description.

**Parameters**:
- `task_id` (int, required): ID of task to update
- `title` (Optional[str], optional): New title (unchanged if None)
- `description` (Optional[str], optional): New description (unchanged if None)

**Returns**: `Task` - The updated task object

**Raises**:
- `ValueError`: If task_id not found
- `ValueError`: If title is invalid when provided (empty, whitespace-only, >200 chars)

**Side Effects**:
- Updates task fields in storage dictionary
- Title validation applied if title is provided
- Description can be set to None (cleared) or any string value

**Edge Cases**:
- Task not found: Raises `ValueError` with message "Task with ID {task_id} not found"
- Both title and description None: Returns unchanged task (no-op)
- Empty string for description: Clears description (sets to empty string)

---

### delete_task

```python
def delete_task(self, task_id: int) -> bool
```

**Description**: Removes a task from storage by its ID.

**Parameters**:
- `task_id` (int, required): ID of task to delete

**Returns**: `bool` - `True` if task was deleted, `False` if not found

**Raises**: None

**Side Effects**:
- Removes task from storage dictionary if found
- No action taken if task_id not found

**Edge Cases**:
- Deleting last task: Returns True, storage becomes empty
- Non-existent ID: Returns False, no exception

---

### toggle_complete

```python
def toggle_complete(self, task_id: int) -> Task
```

**Description**: Toggles the completion status of a task.

**Parameters**:
- `task_id` (int, required): ID of task to toggle

**Returns**: `Task` - The updated task with toggled `completed` status

**Raises**:
- `ValueError`: If task_id not found

**Side Effects**:
- Flips `completed` boolean (True ↔ False)
- Updates task in storage dictionary

**Edge Cases**:
- Task already complete: Sets to incomplete (completed=False)
- Task incomplete: Sets to complete (completed=True)

---

## Error Handling Contract

All methods that can raise `ValueError` MUST provide descriptive error messages:

| Error Condition | Error Message Format |
|-----------------|----------------------|
| Empty title | "Task title cannot be empty" |
| Title too long | "Task title must be 200 characters or less" |
| Task not found | "Task with ID {task_id} not found" |

Error messages should be user-friendly and actionable.

---

## Type Safety

All method signatures use Python type hints:
- Input parameters: `int`, `str`, `Optional[str]`
- Return types: `Task`, `List[Task]`, `bool`
- Raises: `ValueError` (explicitly documented)

Type checking tool: `mypy` recommended (per PEP 8 compliance in plan)

---

## Implementation Compliance

**Code Style** (Plan constraint):
- PEP 8 compliance required
- Type hints on all function signatures
- Docstrings for all methods

**Testing** (Plan constraint):
- Each method must have unit tests
- Test normal cases and edge cases
- Test error conditions and exceptions

**Validation** (FR-009, FR-010):
- Input validation in all methods
- Clear error messages for invalid input
- No silent failures

---

## Evolution Path

**Phase I (Current)**:
- In-memory storage: `Dict[int, Task]`
- Synchronous methods
- No authentication/authorization

**Phase II+ (Future)**:
- Database backend via SQLModel ORM
- Async methods (if needed)
- User context in all operations (multi-tenancy)
- Transaction support for data consistency
