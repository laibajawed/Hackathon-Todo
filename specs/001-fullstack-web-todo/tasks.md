# Tasks: Todo Full-Stack Web Application (Basic Level)

**Input**: Design documents from `/specs/001-fullstack-web-todo/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are NOT included in this task list as they were not explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `phase-2/backend/`
- **Frontend**: `phase-2/frontend/`
- All paths relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create phase-2 directory structure with backend/ and frontend/ subdirectories
- [ ] T002 Initialize FastAPI backend project with requirements.txt (fastapi, uvicorn, sqlmodel, asyncpg, pyjwt, bcrypt, python-dotenv, pydantic[email])
- [ ] T003 [P] Initialize Next.js 16+ frontend project with TypeScript and Tailwind CSS in phase-2/frontend/
- [ ] T004 [P] Create backend .env.example file with DATABASE_URL, JWT_SECRET, ENVIRONMENT, CORS_ORIGINS placeholders
- [ ] T005 [P] Create frontend .env.local.example file with NEXT_PUBLIC_API_URL, BETTER_AUTH_SECRET, NEXT_PUBLIC_APP_URL placeholders
- [ ] T006 [P] Configure Tailwind CSS in phase-2/frontend/tailwind.config.js
- [ ] T007 [P] Configure TypeScript in phase-2/frontend/tsconfig.json with strict mode

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 Create database connection module in phase-2/backend/database.py with async SQLAlchemy engine for Neon PostgreSQL
- [ ] T009 Create User model in phase-2/backend/models.py with id (UUID), email (unique), password_hash, created_at, updated_at fields
- [ ] T010 [P] Create Task model in phase-2/backend/models.py with id (UUID), user_id (FK), title, description, status (enum), created_at, updated_at fields
- [ ] T011 Create database initialization function in phase-2/backend/database.py to create all tables
- [ ] T012 Create JWT verification middleware in phase-2/backend/auth/jwt.py using PyJWT to validate tokens and extract user_id
- [ ] T013 Create FastAPI dependency in phase-2/backend/auth/dependencies.py to get current user ID from JWT token
- [ ] T014 Create password hashing utilities in phase-2/backend/auth/utils.py using bcrypt (cost factor 12)
- [ ] T015 Create Pydantic schemas in phase-2/backend/auth/schemas.py for UserSignup, UserSignin, UserResponse, AuthResponse
- [ ] T016 Create main FastAPI app in phase-2/backend/main.py with CORS middleware configured for frontend origin
- [ ] T017 Create API router structure in phase-2/backend/routes/__init__.py
- [ ] T018 [P] Create TypeScript types in phase-2/frontend/lib/types.ts for User, Task, AuthResponse, TaskStatus

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Registration and Authentication (Priority: P1) 🎯 MVP

**Goal**: Enable users to create accounts and authenticate to receive JWT tokens for API access

**Independent Test**: Register a new user, sign in with credentials, receive JWT token, verify token is required for protected endpoints

### Implementation for User Story 1

- [ ] T019 [P] [US1] Implement POST /api/auth/signup endpoint in phase-2/backend/routes/auth.py to create user with hashed password and return JWT token
- [ ] T020 [P] [US1] Implement POST /api/auth/signin endpoint in phase-2/backend/routes/auth.py to verify credentials and return JWT token
- [ ] T021 [US1] Register auth routes in phase-2/backend/main.py
- [ ] T022 [P] [US1] Configure Better Auth in phase-2/frontend/lib/auth.ts with JWT plugin and secret
- [ ] T023 [P] [US1] Create signup page in phase-2/frontend/app/auth/signup/page.tsx with email/password form
- [ ] T024 [P] [US1] Create signin page in phase-2/frontend/app/auth/signin/page.tsx with email/password form
- [ ] T025 [P] [US1] Create useAuth hook in phase-2/frontend/hooks/useAuth.ts to manage authentication state
- [ ] T026 [US1] Create root layout in phase-2/frontend/app/layout.tsx with auth provider
- [ ] T027 [US1] Create landing page in phase-2/frontend/app/page.tsx with links to signup/signin

**Checkpoint**: At this point, User Story 1 should be fully functional - users can register, sign in, and receive JWT tokens

---

## Phase 4: User Story 2 - View Personal Task List (Priority: P1)

**Goal**: Enable authenticated users to view all their tasks with status indicators, ensuring user isolation

**Independent Test**: Authenticate a user, create several tasks, verify only their tasks appear with correct status indicators

### Implementation for User Story 2

- [ ] T028 [US2] Implement GET /api/tasks endpoint in phase-2/backend/routes/tasks.py to retrieve tasks filtered by authenticated user_id
- [ ] T029 [US2] Add optional status query parameter to GET /api/tasks for filtering by pending/completed
- [ ] T030 [US2] Register task routes in phase-2/backend/main.py
- [ ] T031 [P] [US2] Create API client in phase-2/frontend/lib/api.ts with JWT token attachment to Authorization header
- [ ] T032 [P] [US2] Create useTasks hook in phase-2/frontend/hooks/useTasks.ts for fetching and managing task data
- [ ] T033 [P] [US2] Create TaskItem component in phase-2/frontend/components/TaskItem.tsx to display individual task with status indicator
- [ ] T034 [US2] Create TaskList component in phase-2/frontend/components/TaskList.tsx to display array of tasks
- [ ] T035 [US2] Create AuthGuard component in phase-2/frontend/components/AuthGuard.tsx to protect routes requiring authentication
- [ ] T036 [US2] Create tasks page in phase-2/frontend/app/tasks/page.tsx with TaskList component wrapped in AuthGuard
- [ ] T037 [US2] Add empty state handling in TaskList component for users with no tasks

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can authenticate and view their task list

---

## Phase 5: User Story 3 - Create New Task (Priority: P1)

**Goal**: Enable authenticated users to add new tasks with title and optional description

**Independent Test**: Authenticate a user, submit a new task via form, verify it appears in their task list with pending status

### Implementation for User Story 3

- [ ] T038 [US3] Implement POST /api/tasks endpoint in phase-2/backend/routes/tasks.py to create task associated with authenticated user_id
- [ ] T039 [US3] Add validation in POST /api/tasks to ensure title is not empty (FR-012)
- [ ] T040 [US3] Add input sanitization in POST /api/tasks to prevent XSS attacks (FR-016)
- [ ] T041 [P] [US3] Create Pydantic schemas in phase-2/backend/routes/tasks.py for TaskCreate, TaskUpdate, TaskResponse
- [ ] T042 [P] [US3] Create TaskForm component in phase-2/frontend/components/TaskForm.tsx with title and description inputs
- [ ] T043 [US3] Add form validation in TaskForm component to prevent empty title submission
- [ ] T044 [US3] Integrate TaskForm component into tasks page in phase-2/frontend/app/tasks/page.tsx
- [ ] T045 [US3] Update useTasks hook to include createTask function that calls POST /api/tasks
- [ ] T046 [US3] Add optimistic UI update in TaskForm to show new task immediately before API confirmation

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently - users can authenticate, view tasks, and create new tasks

---

## Phase 6: User Story 4 - Mark Task as Complete/Incomplete (Priority: P2)

**Goal**: Enable authenticated users to toggle task completion status between pending and completed

**Independent Test**: Create a task, toggle its completion status, verify status persists across page refreshes

### Implementation for User Story 4

- [ ] T047 [US4] Implement PATCH /api/tasks/{id}/toggle endpoint in phase-2/backend/routes/tasks.py to toggle task status
- [ ] T048 [US4] Add user_id validation in PATCH endpoint to ensure user owns the task (FR-010)
- [ ] T049 [US4] Update Task model updated_at timestamp on status toggle
- [ ] T050 [P] [US4] Add toggle button/checkbox to TaskItem component in phase-2/frontend/components/TaskItem.tsx
- [ ] T051 [US4] Update useTasks hook to include toggleTaskStatus function that calls PATCH /api/tasks/{id}/toggle
- [ ] T052 [US4] Add visual feedback in TaskItem component for completed tasks (strikethrough, checkmark, color change)
- [ ] T053 [US4] Add optimistic UI update for toggle action to show status change immediately

**Checkpoint**: At this point, User Stories 1-4 should all work independently - users can now track task completion

---

## Phase 7: User Story 5 - Update Task Details (Priority: P2)

**Goal**: Enable authenticated users to modify existing task title and description

**Independent Test**: Create a task, edit its title and description, verify changes are saved and displayed

### Implementation for User Story 5

- [ ] T054 [US5] Implement PUT /api/tasks/{id} endpoint in phase-2/backend/routes/tasks.py to update task title and/or description
- [ ] T055 [US5] Add user_id validation in PUT endpoint to ensure user owns the task (FR-010)
- [ ] T056 [US5] Add validation in PUT endpoint to ensure title is not empty if provided (FR-012)
- [ ] T057 [US5] Add input sanitization in PUT endpoint to prevent XSS attacks (FR-016)
- [ ] T058 [P] [US5] Add edit mode state to TaskItem component in phase-2/frontend/components/TaskItem.tsx
- [ ] T059 [P] [US5] Add inline edit form in TaskItem component with title and description inputs
- [ ] T060 [US5] Update useTasks hook to include updateTask function that calls PUT /api/tasks/{id}
- [ ] T061 [US5] Add save/cancel buttons to edit form in TaskItem component
- [ ] T062 [US5] Add form validation in edit mode to prevent empty title submission

**Checkpoint**: At this point, User Stories 1-5 should all work independently - users can now edit their tasks

---

## Phase 8: User Story 6 - Delete Task (Priority: P3)

**Goal**: Enable authenticated users to permanently remove tasks they no longer need

**Independent Test**: Create a task, delete it with confirmation, verify it no longer appears in the task list

### Implementation for User Story 6

- [ ] T063 [US6] Implement DELETE /api/tasks/{id} endpoint in phase-2/backend/routes/tasks.py to remove task
- [ ] T064 [US6] Add user_id validation in DELETE endpoint to ensure user owns the task (FR-010)
- [ ] T065 [US6] Return 404 error if task doesn't exist or doesn't belong to user
- [ ] T066 [P] [US6] Add delete button to TaskItem component in phase-2/frontend/components/TaskItem.tsx
- [ ] T067 [US6] Update useTasks hook to include deleteTask function that calls DELETE /api/tasks/{id}
- [ ] T068 [US6] Add confirmation dialog before deleting task (browser confirm or custom modal)
- [ ] T069 [US6] Add optimistic UI update to remove task from list immediately after confirmation

**Checkpoint**: All user stories should now be independently functional - complete CRUD operations available

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, environment setup, and final validation

- [ ] T070 [P] Create phase-2/README.md with setup instructions for backend and frontend
- [ ] T071 [P] Create phase-2/backend/.env.example with all required environment variables documented
- [ ] T072 [P] Create phase-2/frontend/.env.local.example with all required environment variables documented
- [ ] T073 [P] Update root CLAUDE.md with Phase 2 usage notes for frontend and backend development
- [ ] T074 [P] Add error handling for expired JWT tokens in phase-2/frontend/lib/api.ts with redirect to signin
- [ ] T075 [P] Add loading states to all async operations in frontend components
- [ ] T076 [P] Add error message display for API failures in frontend components
- [ ] T077 [P] Add responsive design breakpoints in Tailwind CSS for mobile/tablet/desktop (320px-1920px)
- [ ] T078 Verify all API endpoints return appropriate HTTP status codes (200, 201, 401, 404, 500)
- [ ] T079 Verify user isolation by testing with multiple user accounts
- [ ] T080 Run through quickstart.md validation to ensure setup instructions work
- [ ] T081 Create phase-2/docker-compose.yml for optional local development environment (optional)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1 - Auth)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1 - View)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P1 - Create)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 4 (P2 - Toggle)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 5 (P2 - Update)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 6 (P3 - Delete)**: Can start after Foundational (Phase 2) - No dependencies on other stories

**Key Insight**: All user stories are independently implementable after Foundational phase completes!

### Within Each User Story

- Backend endpoints before frontend integration
- API client setup before component implementation
- Core components before page integration
- Validation and error handling after core functionality

### Parallel Opportunities

- **Phase 1**: T003, T004, T005, T006, T007 can run in parallel
- **Phase 2**: T010, T018 can run in parallel after T009
- **Phase 3 (US1)**: T019, T020, T022, T023, T024, T025 can run in parallel
- **Phase 4 (US2)**: T031, T032, T033 can run in parallel
- **Phase 5 (US3)**: T041, T042 can run in parallel
- **Phase 6 (US4)**: T050 can run in parallel with backend work
- **Phase 7 (US5)**: T058, T059 can run in parallel with backend work
- **Phase 8 (US6)**: T066 can run in parallel with backend work
- **Phase 9**: T070, T071, T072, T073, T074, T075, T076, T077 can run in parallel
- **Once Foundational completes**: All user stories (Phase 3-8) can be worked on in parallel by different team members

---

## Parallel Example: User Story 1 (Authentication)

```bash
# Launch backend auth endpoints together:
Task: "Implement POST /api/auth/signup endpoint in phase-2/backend/routes/auth.py"
Task: "Implement POST /api/auth/signin endpoint in phase-2/backend/routes/auth.py"

# Launch frontend auth pages together:
Task: "Configure Better Auth in phase-2/frontend/lib/auth.ts"
Task: "Create signup page in phase-2/frontend/app/auth/signup/page.tsx"
Task: "Create signin page in phase-2/frontend/app/auth/signin/page.tsx"
Task: "Create useAuth hook in phase-2/frontend/hooks/useAuth.ts"
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Authentication)
4. Complete Phase 4: User Story 2 (View Tasks)
5. Complete Phase 5: User Story 3 (Create Tasks)
6. **STOP and VALIDATE**: Test all three P1 stories independently
7. Deploy/demo MVP with core functionality

**MVP Delivers**: Users can register, sign in, view their tasks, and create new tasks - a complete basic todo app!

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (Auth) → Test independently → Deploy/Demo
3. Add User Story 2 (View) → Test independently → Deploy/Demo
4. Add User Story 3 (Create) → Test independently → Deploy/Demo (MVP!)
5. Add User Story 4 (Toggle) → Test independently → Deploy/Demo
6. Add User Story 5 (Update) → Test independently → Deploy/Demo
7. Add User Story 6 (Delete) → Test independently → Deploy/Demo (Complete!)
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Auth)
   - Developer B: User Story 2 (View) + User Story 3 (Create)
   - Developer C: User Story 4 (Toggle) + User Story 5 (Update) + User Story 6 (Delete)
3. Stories complete and integrate independently
4. Final integration testing with all stories

---

## Task Summary

**Total Tasks**: 81 tasks

**Tasks by Phase**:
- Phase 1 (Setup): 7 tasks
- Phase 2 (Foundational): 11 tasks
- Phase 3 (US1 - Auth): 9 tasks
- Phase 4 (US2 - View): 10 tasks
- Phase 5 (US3 - Create): 9 tasks
- Phase 6 (US4 - Toggle): 7 tasks
- Phase 7 (US5 - Update): 9 tasks
- Phase 8 (US6 - Delete): 7 tasks
- Phase 9 (Polish): 12 tasks

**Parallelizable Tasks**: 32 tasks marked with [P]

**MVP Scope** (Recommended first delivery):
- Phase 1: Setup (7 tasks)
- Phase 2: Foundational (11 tasks)
- Phase 3: User Story 1 - Auth (9 tasks)
- Phase 4: User Story 2 - View (10 tasks)
- Phase 5: User Story 3 - Create (9 tasks)
- **Total MVP: 46 tasks**

**Independent Test Criteria**:
- US1: Register user, sign in, receive JWT, verify token required
- US2: Authenticate, view tasks, verify user isolation
- US3: Authenticate, create task, verify it appears in list
- US4: Create task, toggle status, verify persistence
- US5: Create task, edit details, verify changes saved
- US6: Create task, delete it, verify removal

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Tests are NOT included as they were not explicitly requested in the specification
- All paths are relative to repository root
- Backend uses Python 3.13+ with FastAPI
- Frontend uses Next.js 16+ with TypeScript and Tailwind CSS
- Database is Neon Serverless PostgreSQL
- Authentication uses Better Auth with JWT tokens
