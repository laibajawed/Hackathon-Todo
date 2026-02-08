# Tasks: Phase I Console Todo Application

**Input**: Design documents from `/specs/001-console-todo-app/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md, contracts/todo-manager-interface.md

**Tests**: Tests are OPTIONAL - not explicitly requested in feature specification. Test tasks not included in this breakdown.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `phase-1-console/`, `phase-1-console/src/`, `phase-1-console/tests/`
- All paths shown are absolute from repository root

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create phase-1-console directory structure per implementation plan (phase-1-console/src/{models,manager,cli}, phase-1-console/tests)
- [X] T002 Initialize Python 3.13+ project with uv in phase-1-console directory (pyproject.toml with pytest dependency)
- [X] T003 [P] Create __init__.py files for phase-1-console/src, phase-1-console/src/models, phase-1-console/src/manager, phase-1-console/src/cli, phase-1-console/tests
- [X] T004 [P] Create README.md with basic usage instructions in phase-1-console/README.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create TaskModel dataclass in phase-1-console/src/models/task.py (id, title, description, completed, created_at attributes with validation)

**Checkpoint**: Foundation ready - TaskModel available for all user story implementation

---

## Phase 3: User Story 1 - Add and View Tasks (Priority: P1) 🎯 MVP

**Goal**: Enable users to create tasks with titles and optional descriptions, and see all tasks in a list view

**Independent Test**: Launch application, create several tasks with various attributes, and display them. Can verify task creation and listing works independently of other stories.

### Implementation for User Story 1

- [X] T006 [US1] Implement TodoManager.__init__ method in phase-1-console/src/manager/todo_manager.py (initialize empty Dict[int, Task] storage)
- [X] T007 [US1] Implement TodoManager.add_task method in phase-1-console/src/manager/todo_manager.py (validate title 1-200 chars, assign incremental ID, set created_at, return Task)
- [X] T008 [US1] Implement TodoManager.list_tasks method in phase-1-console/src/manager/todo_manager.py (return List[Task] ordered by ID, handle empty list gracefully)
- [X] T009 [US1] Create CLIHandler class in phase-1-console/src/cli/handler.py (main loop, menu display, input capture)
- [X] T010 [US1] Implement CLIHandler add task menu option in phase-1-console/src/cli/handler.py (prompt for title/description, call TodoManager.add_task, display result/error)
- [X] T011 [US1] Implement CLIHandler view tasks menu option in phase-1-console/src/cli/handler.py (call TodoManager.list_tasks, format and display with ID, status, title, description)
- [X] T012 [US1] Create application entry point in phase-1-console/main.py (import CLIHandler, instantiate, run main loop)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can add tasks and view their list. MVP is deliverable.

---

## Phase 4: User Story 2 - Update and Delete Tasks (Priority: P2)

**Goal**: Enable users to modify task details and remove tasks from the list

**Independent Test**: Create tasks, then modify their titles/descriptions and delete specific tasks by ID, confirming changes are reflected in list without breaking add/view functionality.

### Implementation for User Story 2

- [X] T013 [US2] Implement TodoManager.update_task method in phase-1-console/src/manager/todo_manager.py (update title/description by ID, validate new title if provided, handle not found)
- [X] T014 [US2] Implement TodoManager.delete_task method in phase-1-console/src/manager/todo_manager.py (remove task by ID, return True/False, handle empty list after deletion)
- [X] T015 [US2] Implement CLIHandler update task menu option in phase-1-console/src/cli/handler.py (prompt for ID and new title/description, call TodoManager.update_task, display success/error)
- [X] T016 [US2] Implement CLIHandler delete task menu option in phase-1-console/src/cli/handler.py (prompt for ID, call TodoManager.delete_task, display success/error)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - users can add, view, update, and delete tasks.

---

## Phase 5: User Story 3 - Mark Tasks as Complete (Priority: P3)

**Goal**: Enable users to toggle task completion status and track progress

**Independent Test**: Create tasks, mark them as complete/uncomplete, and verify status indicators change appropriately in the task list without breaking add/view/update/delete functionality.

### Implementation for User Story 3

- [X] T017 [US3] Implement TodoManager.toggle_complete method in phase-1-console/src/manager/todo_manager.py (toggle completed boolean by ID, handle not found)
- [X] T018 [US3] Implement CLIHandler toggle complete menu option in phase-1-console/src/cli/handler.py (prompt for ID, call TodoManager.toggle_complete, display success/error)
- [X] T019 [US3] Implement CLIHandler exit functionality in phase-1-console/src/cli/handler.py (exit infinite loop gracefully on menu selection)

**Checkpoint**: All user stories should now be independently functional - full CRUD operations plus completion tracking.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Code quality, validation, and completeness

- [X] T020 [P] Add comprehensive error messages throughout TodoManager methods per contracts (empty title, title too long, task not found)
- [X] T021 [P] Add input validation in CLIHandler for non-numeric task IDs and edge cases
- [X] T022 Verify single-command startup works (python main.py launches application without setup steps)
- [X] T023 Add PEP 8 compliance check (run ruff check, fix any issues)
- [X] T024 Add type hints verification (run mypy, ensure all methods have type hints)
- [X] T025 Validate all acceptance scenarios from spec.md pass manually
- [X] T026 Test edge cases: empty task list, invalid IDs, whitespace in input, special characters in descriptions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion (TaskModel)
  - User stories can proceed sequentially in priority order (P1 → P2 → P3)
  - Each story should be independently testable before moving to next
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories. MVP scope.
- **User Story 2 (P2)**: Can start after US1 complete - Adds update/delete methods to existing TodoManager and CLIHandler
- **User Story 3 (P3)**: Can start after US2 complete - Adds toggle_complete method and exit functionality

### Within Each User Story

- TodoManager methods before CLIHandler methods that use them
- Core implementation before error handling refinements
- Each story complete before moving to next priority

### Parallel Opportunities

- Setup tasks T003, T004 can run in parallel (different files, no dependencies)
- Polish tasks T020, T021 can run in parallel (different areas)

---

## Parallel Example: Setup Phase

```bash
# Launch Setup Phase 3 and T004 together:
Task: "T003 [P] Create __init__.py files for all packages"
Task: "T004 [P] Create README.md with basic usage instructions"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005 - TaskModel)
3. Complete Phase 3: User Story 1 (T006-T012)
4. **STOP and VALIDATE**: Test User Story 1 independently - create tasks, view tasks, verify MVP works
5. Demo MVP functionality

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (T001-T005)
2. Add User Story 1 → Test independently → MVP deliverable (T006-T012)
3. Add User Story 2 → Test independently → Adds update/delete capability (T013-T016)
4. Add User Story 3 → Test independently → Adds completion tracking (T017-T019)
5. Polish and validate all acceptance scenarios (T020-T026)
6. Each story adds value without breaking previous stories

### Sequential Story Flow

**Recommended execution order:**
- US1 (Add/View): Creates TodoManager基础, CLIHandler basic structure, main entry point
- US2 (Update/Delete): Extends TodoManager and CLIHandler with modification methods
- US3 (Complete): Extends TodoManager and CLIHandler with completion toggle and exit

**Why not parallel stories:**
- TodoManager is built incrementally across stories
- CLIHandler menu options accumulate per story
- Smallest change principle favors sequential additions
- Each story's methods depend on previous story's implementations

---

## Notes

- [P] tasks = different files, no dependencies within same phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- User Story 1 alone provides minimum viable product
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Verify all acceptance scenarios from spec.md before final polish
- All file paths are absolute from repository root
- Tests not included as they were not explicitly requested in feature specification
