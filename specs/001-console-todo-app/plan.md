# Implementation Plan: Phase I Console Todo Application

**Branch**: `001-console-todo-app` | **Date**: 2026-01-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-console-todo-app/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build an in-memory CLI todo application with simple layered architecture: TaskModel dataclass, TodoManager for CRUD logic, and CLIHandler for user interaction. The application stores tasks in a Python list/dict, supports add/view/update/delete/complete operations, and validates input according to spec requirements (1-200 char titles, optional descriptions, incremental IDs).

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: `uv` (dependency management), `datetime` (standard library)
**Storage**: Python list/dict (in-memory, no external database per Phase I scope)
**Testing**: pytest (standard Python testing framework)
**Target Platform**: WSL 2 / Linux terminal
**Project Type**: single (CLI application)
**Performance Goals**: Task operations complete in under 2 seconds (from SC-002), task creation under 10 seconds (from SC-001)
**Constraints**: In-memory only (data loss on exit), PEP 8 code style, type hints on all functions, single command startup (`python main.py`)
**Scale/Scope**: Single user, in-memory storage sufficient for Phase I (evolves to PostgreSQL in later phases per Constitution)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Constitutional Principles Review

| Principle | Status | Justification |
|-----------|--------|--------------|
| Spec-First, Code-Second | ✅ PASS | This plan follows spec → plan sequence; no code will be written without this plan |
| Zero Boilerplate | ✅ PASS | All scaffolding and code will be AI-generated (agents) - no manual coding per constitution |
| Deterministic Evolution | ✅ PASS | This is CLI Phase I - builds foundation before web UI/API phases. In-memory storage is appropriate Phase I scope, evolves to PostgreSQL in later phases |
| Agent-Native Design | ✅ PASS | CLI interface designed for human use; MCP tools will be added in later chatbot phase per evolution path |

### Technology Stack Constraints

| Constraint | Status | Justification |
|------------|--------|--------------|
| Python 3.13+ | ✅ PASS | Using Python 3.13+ as specified in user input and aligns with constitution |
| SQLModel + PostgreSQL | ✅ PASS | Phase I uses in-memory storage (per spec and evolution path); SQLModel/PostgreSQL added in later phases per Constitution |
| FastAPI | ⚠️ NOT APPLICABLE | CLI phase does not require FastAPI; framework added in web API phase |

### Authentication & Authorization

| Constraint | Status | Justification |
|------------|--------|--------------|
| JWT-based Better Auth | ✅ PASS | Phase I is single-user CLI; multi-tenancy and authentication added in later phases per Constitution |

### Deployment Architecture

| Constraint | Status | Justification |
|------------|--------|--------------|
| Minikube/DOKS | ✅ PASS | Not applicable for CLI Phase I; cloud deployment in later phases |

### Development Workflow

| Constraint | Status | Justification |
|------------|--------|--------------|
| AI-assisted DevOps | ✅ PASS | Not applicable for CLI Phase I; AI tooling for k8s in later phases |

### Non-Goals Compliance

| Non-Goal | Status | Justification |
|----------|--------|--------------|
| Mobile apps | ✅ PASS | CLI only, no mobile apps |
| Alternative DBs | ✅ PASS | Phase I uses in-memory; PostgreSQL in later phases per constitution |
| Manual DevOps | ✅ PASS | No DevOps required for CLI Phase I |

**CONSTITUTION CHECK RESULT**: ✅ **PASS** - All applicable constraints satisfied. Phase I CLI implementation is consistent with Deterministic Evolution path.

## Project Structure

### Documentation (this feature)

```text
specs/001-console-todo-app/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   └── todo-manager-interface.md  # TodoManager method contracts
├── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
└── checklists/
    └── requirements.md  # Specification quality checklist (already created)
```

### Source Code (repository root)

```text
phase-1-console/
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py              # TaskModel dataclass
│   ├── manager/
│   │   ├── __init__.py
│   │   └── todo_manager.py      # TodoManager CRUD logic
│   └── cli/
│       ├── __init__.py
│       └── handler.py           # CLIHandler main loop and input/output
├── tests/
│   ├── __init__.py
│   ├── test_task_model.py       # TaskModel unit tests
│   ├── test_todo_manager.py     # TodoManager unit tests
│   └── test_cli_handler.py      # CLIHandler integration tests
├── main.py                      # Application entry point
├── pyproject.toml               # Project configuration with uv
└── README.md                    # Basic usage instructions
```

**Structure Decision**: Single project structure with clear separation of concerns:
- `models/` - Data structures (TaskModel)
- `manager/` - Business logic (TodoManager)
- `cli/` - User interface (CLIHandler)
- `tests/` - Test coverage aligned with source structure
- Entry point at `main.py` for single-command execution

This structure aligns with Simple Layered Architecture from user input and supports evolution to future phases.

## Phase 0: Research & Technology Decisions

*Status*: COMPLETE (no unresolved clarifications)

### Research Findings

No NEEDS CLARIFICATION items were identified. Technical decisions based on:
- User input explicitly specified: Python 3.13+, layered architecture, in-memory storage
- Constitution confirms Python 3.13+ as required language
- Spec explicitly requires in-memory storage for Phase I (evolves to PostgreSQL later)
- Standard library used where possible (datetime, list, dict)
- pytest as de facto standard Python testing framework

### Architecture Decision: In-Memory Storage for Phase I

**Decision**: Use Python list/dict for task storage in Phase I

**Rationale**:
- Spec explicitly requires in-memory storage for Phase I
- Simplifies initial implementation and testing
- Aligns with Constitution's "Deterministic Evolution" principle - builds foundation before adding database layer
- Supports all CRUD operations efficiently for single-user CLI use case

**Alternatives Considered**:
- SQLite: Rejected - spec requires in-memory only
- PostgreSQL: Rejected - Constitution's SQLModel/Neon stack applies to later phases; Phase I scope is CLI with in-memory storage per spec

**Evolution Path**:
Phase I (CLI) → Phase II+ (API with PostgreSQL via SQLModel per Constitution)

### Architecture Decision: Layered Architecture

**Decision**: Implement simple layered architecture with TaskModel, TodoManager, CLIHandler

**Rationale**:
- Explicitly specified in user input
- Clear separation of concerns: data → logic → interface
- Supports testing at each layer independently
- Foundation for evolution to web API (TodoManager can be reused with different interface layer)

**Alternatives Considered**:
- Monolithic single file: Rejected - harder to test, doesn't scale to later phases
- Repository pattern: Rejected - over-engineering for Phase I in-memory storage

## Phase 1: Design & Contracts

### Data Model

See [data-model.md](./data-model.md) for complete entity definitions, validation rules, and state transitions.

### API Contracts

CLI interface contracts documented in [contracts/todo-manager-interface.md](./contracts/todo-manager-interface.md).

### Quickstart Guide

See [quickstart.md](./quickstart.md) for development setup and running the application.

## Complexity Tracking

> No constitutional violations requiring justification. All design choices align with principles and Phase I scope.
