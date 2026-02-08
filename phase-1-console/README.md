# Phase I Console Todo Application

In-memory CLI todo application for task tracking.

## Prerequisites

- Python 3.13+
- pytest (for testing)

## Running the Application

```bash
python main.py
```

## Features

- Add tasks with titles and optional descriptions
- View all tasks in a list
- Update task titles and descriptions
- Delete tasks
- Mark tasks as complete
- Input validation (1-200 character titles)

## Structure

- `src/models/` - Task dataclass
- `src/manager/` - TodoManager business logic
- `src/cli/` - CLIHandler interface
- `tests/` - Test files
