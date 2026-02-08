# Quickstart Guide: Phase I Console Todo Application

**Feature**: 001-console-todo-app
**Phase**: Phase I (In-Memory CLI)
**Last Updated**: 2026-01-06

## Prerequisites

- **Python**: Version 3.13 or higher
- **uv**: Python package and project manager (https://github.com/astral-sh/uv)
- **Platform**: WSL 2 (Windows) or Linux terminal
- **Terminal**: Any POSIX-compatible terminal

---

## Development Setup

### 1. Install uv (if not already installed)

```bash
# On Linux/WSL
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv
```

### 2. Navigate to Phase I directory

```bash
cd phase-1-console
```

### 3. Create project structure

The project structure should be:

```
phase-1-console/
├── src/
│   ├── __init__.py
│   ├── models/
│   ├── manager/
│   └── cli/
├── tests/
├── main.py
├── pyproject.toml
└── README.md
```

### 4. Initialize project with uv

```bash
# Initialize project
uv init --no-readme

# Create directory structure
mkdir -p src/models src/manager src/cli tests
touch src/__init__.py src/models/__init__.py src/manager/__init__.py src/cli/__init__.py tests/__init__.py
```

### 5. Install dependencies

For Phase I, dependencies are minimal:

```bash
# Add development dependencies
uv add --dev pytest

# No runtime dependencies required (uses Python standard library)
```

### 6. Verify installation

```bash
# Check Python version (should be 3.13+)
python --version

# Run uv check
uv check
```

---

## Running the Application

### Single Command Startup

```bash
python main.py
```

The application will launch and display a menu with available options.

### Expected Menu

```
=== Todo Manager ===

1. Add Task
2. View Tasks
3. Update Task
4. Delete Task
5. Mark as Complete
6. Exit

Enter your choice (1-6):
```

### Usage Flow

#### Adding a Task

1. Select option 1 (Add Task)
2. Enter task title (1-200 characters)
3. Optionally enter a description (press Enter to skip)
4. Task is created with auto-assigned ID

#### Viewing Tasks

1. Select option 2 (View Tasks)
2. All tasks displayed with:
   - ID
   - Completion status: `[ ]` (pending) or `[x]` (complete)
   - Title
   - Description (if present)
   - Created timestamp

#### Updating a Task

1. Select option 3 (Update Task)
2. Enter task ID to update
3. Enter new title (or press Enter to keep current)
4. Enter new description (or press Enter to keep current)

#### Deleting a Task

1. Select option 4 (Delete Task)
2. Enter task ID to delete
3. Task is removed from list

#### Marking Task as Complete

1. Select option 5 (Mark as Complete)
2. Enter task ID to toggle completion
3. Task status flips between pending and complete

#### Exiting

1. Select option 6 (Exit)
2. Application terminates gracefully

---

## Running Tests

### Run all tests

```bash
# Using uv to run pytest
uv run pytest

# With verbose output
uv run pytest -v

# With coverage
uv run pytest --cov=src --cov-report=html
```

### Run specific test file

```bash
uv run pytest tests/test_todo_manager.py
uv run pytest tests/test_task_model.py
uv run pytest tests/test_cli_handler.py
```

### Run with specific pattern

```bash
# Run only unit tests
uv run pytest tests/ -m unit

# Run only integration tests
uv run pytest tests/ -m integration
```

---

## Code Quality

### Type Checking

```bash
# Install mypy
uv add --dev mypy

# Run type checking
uv run mypy src/
```

### Linting

```bash
# Install ruff
uv add --dev ruff

# Check code style (PEP 8 compliance)
uv run ruff check src/

# Auto-fix issues
uv run ruff check --fix src/

# Format code
uv run ruff format src/
```

---

## Project Structure Reference

```
phase-1-console/
│
├── src/
│   ├── models/
│   │   └── task.py              # TaskModel dataclass definition
│   ├── manager/
│   │   └── todo_manager.py      # TodoManager business logic
│   └── cli/
│       └── handler.py           # CLIHandler main loop and UI
│
├── tests/
│   ├── test_task_model.py       # TaskModel unit tests
│   ├── test_todo_manager.py     # TodoManager unit tests
│   └── test_cli_handler.py      # CLIHandler integration tests
│
├── main.py                      # Application entry point
├── pyproject.toml               # uv project configuration
└── README.md                    # Basic documentation
```

---

## Common Issues

### Issue: "Module not found" error

**Solution**: Make sure you're running commands from the `phase-1-console` directory and that virtual environment is activated (or using `uv run`).

### Issue: Python version too old

**Solution**:
```bash
# Install Python 3.13 using uv
uv python install 3.13

# Set as project default
uv python pin 3.13
```

### Issue: Tests fail with "No module named 'src'"

**Solution**: Ensure `src/__init__.py` exists and you're running from the project root:
```bash
python -m pytest tests/  # Alternative method
```

---

## Next Steps

After implementation is complete:

1. Review success criteria in [spec.md](./spec.md)
2. Run full test suite
3. Test application manually through all user stories
4. Check for PEP 8 compliance
5. Validate all acceptance scenarios pass

---

## Evolution to Next Phase

Phase I is a stepping stone. When ready to move to Phase II (Web API):

- TodoManager logic can be reused
- In-memory storage will be replaced with PostgreSQL (SQLModel)
- CLIHandler will be replaced with FastAPI endpoints
- Authentication and multi-tenancy added per constitution
