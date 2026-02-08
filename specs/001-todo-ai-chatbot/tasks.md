# Tasks: Todo AI Chatbot

**Input**: Design documents from `/specs/001-todo-ai-chatbot/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL and not included in this task breakdown as they were not explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `phase-3/backend/`
- **Frontend**: `phase-3/frontend/`
- All paths are relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create phase-3 directory structure per plan.md (backend/, frontend/, README.md, CLAUDE.md)
- [X] T002 [P] Initialize backend Python project with requirements.txt in phase-3/backend/
- [X] T003 [P] Initialize frontend Next.js project with package.json in phase-3/frontend/
- [X] T004 [P] Create backend .env.example with DATABASE_URL, JWT_SECRET, GROQ_API_KEY in phase-3/backend/
- [X] T005 [P] Create frontend .env.local.example with NEXT_PUBLIC_API_URL, BETTER_AUTH_SECRET in phase-3/frontend/
- [X] T006 [P] Configure Python linting (ruff, black) in phase-3/backend/
- [X] T007 [P] Configure TypeScript and ESLint in phase-3/frontend/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database & Models

- [X] T008 Create Conversation model in phase-3/backend/models.py (id, user_id, title, created_at, updated_at, is_active, total_tokens, message_count)
- [X] T009 Create Message model in phase-3/backend/models.py (id, conversation_id, role, content, token_count, created_at, sequence_number)
- [X] T010 Create Alembic migration for conversations and messages tables in phase-3/backend/alembic/versions/
- [X] T011 Add database indexes per data-model.md (idx_user_active, idx_conversation_sequence, idx_conversation_created)

### Authentication & Middleware

- [X] T012 [P] Implement JWT validation middleware in phase-3/backend/auth.py (validate_jwt, get_current_user)
- [X] T013 [P] Add user_id extraction from JWT in phase-3/backend/auth.py

### OpenAI Agents SDK Infrastructure

- [X] T014 Install openai-agents[litellm] in phase-3/backend/requirements.txt
- [X] T015 Create tools directory structure in phase-3/backend/tools/
- [X] T016 Create base tool utilities in phase-3/backend/tools/__init__.py (user ownership verification, error handling, export all tools)

### Agent Runner with OpenAI Agents SDK

- [X] T017 Create agent configuration in phase-3/backend/agent/runner.py with OpenAI Agents SDK and LiteLLM
- [X] T018 Configure Groq via LiteLLM in phase-3/backend/agent/runner.py (model: groq/llama-3.1-8b-instant)
- [X] T019 Create agent instructions for todo task management in phase-3/backend/agent/runner.py
- [X] T020 Implement run_agent function in phase-3/backend/agent/runner.py (use Runner.run with agent and user message)
- [X] T020a Add confirmation message handling in agent instructions in phase-3/backend/agent/runner.py
- [X] T020b Add ambiguous command handling in agent instructions in phase-3/backend/agent/runner.py
- [X] T020c Add clarification prompt patterns in agent instructions in phase-3/backend/agent/runner.py

### API Infrastructure

- [X] T021 Create FastAPI router for chat endpoints in phase-3/backend/routes/chat.py
- [X] T022 Add CORS middleware configuration in phase-3/backend/main.py (allow localhost:3000)
- [X] T023 Create database connection pool in phase-3/backend/database.py (Neon PostgreSQL)
- [X] T024 Add error handling middleware in phase-3/backend/main.py (catch exceptions, return ErrorResponse)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add Tasks via Natural Language (Priority: P1) 🎯 MVP

**Goal**: Users can create new tasks by describing them in natural language without needing to fill out forms or follow specific syntax.

**Independent Test**: Send conversational messages like "Add buy groceries to my list" or "Remind me to call mom tomorrow" and verify tasks are created correctly.

### Function Tool Implementation

- [X] T025 [P] [US1] Create CreateTaskInput Pydantic model in phase-3/backend/tools/create_task.py
- [X] T026 [P] [US1] Implement create_task function with @function_tool decorator in phase-3/backend/tools/create_task.py
- [X] T027 [US1] Add input validation in create_task (title length 1-200, description max 2000) in phase-3/backend/tools/create_task.py
- [X] T028 [US1] Add HTML escaping for XSS prevention in create_task in phase-3/backend/tools/create_task.py
- [X] T029 [US1] Add user ownership verification in create_task in phase-3/backend/tools/create_task.py
- [X] T030 [US1] Register create_task tool with agent in phase-3/backend/agent/runner.py

### Agent Integration

- [X] T031 [US1] Update agent instructions to handle task creation intents in phase-3/backend/agent/runner.py
- [X] T032 [US1] Test create_task tool invocation through OpenAI Agents SDK in phase-3/backend/agent/runner.py (map intent to MCP tool invocation)

### Chat Endpoint

- [X] T033 [US1] Implement POST /api/{user_id}/chat endpoint in phase-3/backend/routes/chat.py (accept ChatRequest, return ChatResponse)
- [X] T034 [US1] Add JWT validation to chat endpoint in phase-3/backend/routes/chat.py (verify user_id matches token)
- [X] T035 [US1] Implement conversation creation logic in phase-3/backend/routes/chat.py (create new conversation if none active)
- [X] T036 [US1] Integrate OpenAI Agents SDK Runner.run in chat endpoint in phase-3/backend/routes/chat.py
- [X] T037 [US1] Implement message persistence in phase-3/backend/routes/chat.py (save user message and assistant response)
- [X] T038 [US1] Add token counting for messages in phase-3/backend/routes/chat.py (use tiktoken for estimation)
- [X] T039 [US1] Add error handling for chat endpoint in phase-3/backend/routes/chat.py (handle Groq API errors, tool errors)

### Frontend Chat UI

- [X] T040 [P] [US1] Create ChatWindow component in phase-3/frontend/components/ChatWindow.tsx (message list, input field, send button)
- [X] T041 [P] [US1] Create chat API client in phase-3/frontend/services/chatApi.ts (sendMessage function with JWT header)
- [X] T042 [US1] Create chat page in phase-3/frontend/app/chat/page.tsx (render ChatWindow, handle authentication)
- [X] T043 [US1] Add message state management in phase-3/frontend/components/ChatWindow.tsx (useState for messages array)
- [X] T044 [US1] Implement message sending in phase-3/frontend/components/ChatWindow.tsx (call chatApi.sendMessage, update state)
- [X] T045 [US1] Add loading state during message send in phase-3/frontend/components/ChatWindow.tsx (disable input, show spinner)
- [X] T046 [US1] Add error handling for failed messages in phase-3/frontend/components/ChatWindow.tsx (display error toast)
- [X] T047 [US1] Style chat interface with Tailwind CSS in phase-3/frontend/components/ChatWindow.tsx (responsive design, message bubbles)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can add tasks via natural language and receive confirmation

---

## Phase 4: User Story 2 - View and Query Tasks (Priority: P2)

**Goal**: Users can ask about their tasks in natural language and receive relevant information about their todo list.

**Independent Test**: Ask questions like "What's on my todo list?", "Show me my tasks", or "What do I need to do today?" and verify the chatbot returns the correct task list.

### Function Tool Implementation

- [X] T048 [P] [US2] Create ListTasksInput Pydantic model in phase-3/backend/tools/list_tasks.py
- [X] T049 [P] [US2] Implement list_tasks function with @function_tool decorator in phase-3/backend/tools/list_tasks.py
- [X] T050 [US2] Add status filtering logic (pending/completed) in list_tasks in phase-3/backend/tools/list_tasks.py
- [X] T051 [US2] Add limit parameter handling (default 50, max 100) in list_tasks in phase-3/backend/tools/list_tasks.py
- [X] T052 [US2] Add user ownership verification in list_tasks in phase-3/backend/tools/list_tasks.py
- [X] T053 [US2] Format task list response with all task details in list_tasks in phase-3/backend/tools/list_tasks.py
- [X] T054 [US2] Register list_tasks tool with agent in phase-3/backend/agent/runner.py

### Agent Integration

- [X] T055 [US2] Update agent instructions to handle task viewing intents in phase-3/backend/agent/runner.py
- [X] T056 [US2] Test list_tasks tool invocation through OpenAI Agents SDK in phase-3/backend/agent/runner.py

### Frontend Enhancement

- [X] T057 [US2] Add task list rendering in chat messages in phase-3/frontend/components/ChatWindow.tsx (display tasks in structured format)
- [X] T058 [US2] Add empty state handling in phase-3/frontend/components/ChatWindow.tsx (show "No tasks" message)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can add and view tasks

---

## Phase 5: User Story 6 - Maintain Conversation Context (Priority: P2)

**Goal**: The chatbot remembers the conversation context within a session, allowing users to have natural multi-turn conversations without repeating information.

**Independent Test**: Have a multi-turn conversation like "Add buy groceries" followed by "Actually, make that organic groceries" and verify the system understands "that" refers to the just-created task.

### Conversation Management

- [X] T059 [US6] Implement conversation retrieval logic in phase-3/backend/routes/chat.py (get active conversation for user)
- [X] T060 [US6] Implement conversation history loading in phase-3/backend/routes/chat.py (load last N messages for context)
- [X] T061 [US6] Pass conversation history to OpenAI Agents SDK Runner in phase-3/backend/routes/chat.py
- [X] T062 [US6] Implement context window management in phase-3/backend/agent/runner.py (limit context to prevent token overflow)

### History Endpoint

- [X] T063 [P] [US6] Implement GET /api/{user_id}/chat/history endpoint in phase-3/backend/routes/chat.py (return HistoryResponse)
- [X] T064 [US6] Add pagination support for history in phase-3/backend/routes/chat.py (limit, offset parameters)
- [X] T065 [US6] Add JWT validation to history endpoint in phase-3/backend/routes/chat.py

### New Conversation Endpoint

- [X] T066 [P] [US6] Implement POST /api/{user_id}/chat/new endpoint in phase-3/backend/routes/chat.py (deactivate current, create new)
- [X] T067 [US6] Add conversation deactivation logic in phase-3/backend/routes/chat.py (set is_active=false on old conversation)

### Logout & Session Cleanup

- [X] T068 [P] [US6] Implement POST /api/{user_id}/logout endpoint in phase-3/backend/routes/chat.py (delete all user conversations and messages)
- [X] T069 [US6] Add JWT validation to logout endpoint in phase-3/backend/routes/chat.py
- [X] T070 [US6] Add cascade delete logic in phase-3/backend/routes/chat.py (delete conversations, cascade to messages per FR-015)

### Frontend Enhancement

- [X] T071 [US6] Load conversation history on mount in phase-3/frontend/components/ChatWindow.tsx (call history endpoint)
- [X] T072 [US6] Add "New Conversation" button in phase-3/frontend/components/ChatWindow.tsx (call new conversation endpoint)
- [X] T073 [US6] Display conversation history in chat window in phase-3/frontend/components/ChatWindow.tsx (render previous messages)

**Checkpoint**: At this point, conversation context is maintained - users can have natural multi-turn conversations

---

## Phase 6: User Story 3 - Mark Tasks Complete (Priority: P3)

**Goal**: Users can mark tasks as complete through conversational commands without navigating through UI elements.

**Independent Test**: Say "Mark buy groceries as done" or "I finished calling mom" and verify the task status updates correctly.

### Function Tool Implementation

- [X] T074 [P] [US3] Create ToggleTaskStatusInput Pydantic model in phase-3/backend/tools/toggle_task_status.py
- [X] T075 [P] [US3] Implement toggle_task_status function with @function_tool decorator in phase-3/backend/tools/toggle_task_status.py
- [X] T076 [US3] Add status toggle logic (pending↔completed) in toggle_task_status in phase-3/backend/tools/toggle_task_status.py
- [X] T077 [US3] Add user ownership verification in toggle_task_status in phase-3/backend/tools/toggle_task_status.py
- [X] T078 [US3] Add task not found error handling in toggle_task_status in phase-3/backend/tools/toggle_task_status.py
- [X] T079 [US3] Register toggle_task_status tool with agent in phase-3/backend/agent/runner.py

### Agent Integration

- [X] T080 [US3] Update agent instructions to handle task completion intents in phase-3/backend/agent/runner.py
- [X] T081 [US3] Add context-based task resolution in agent instructions (resolve "that task", "the first one") in phase-3/backend/agent/runner.py
- [X] T082 [US3] Test toggle_task_status tool invocation through OpenAI Agents SDK in phase-3/backend/agent/runner.py

**Checkpoint**: Users can now mark tasks complete via natural language

---

## Phase 7: User Story 4 - Update Task Details (Priority: P4)

**Goal**: Users can modify existing tasks through natural language commands.

**Independent Test**: Say "Change buy groceries to buy organic groceries" and verify the task title updates correctly.

### Function Tool Implementation

- [X] T083 [P] [US4] Create UpdateTaskInput Pydantic model in phase-3/backend/tools/update_task.py
- [X] T084 [P] [US4] Implement update_task function with @function_tool decorator in phase-3/backend/tools/update_task.py
- [X] T085 [US4] Add input validation (title length, description length) in update_task in phase-3/backend/tools/update_task.py
- [X] T086 [US4] Add HTML escaping for XSS prevention in update_task in phase-3/backend/tools/update_task.py
- [X] T087 [US4] Add user ownership verification in update_task in phase-3/backend/tools/update_task.py
- [X] T088 [US4] Add task not found error handling in update_task in phase-3/backend/tools/update_task.py
- [X] T089 [US4] Register update_task tool with agent in phase-3/backend/agent/runner.py

### Agent Integration

- [X] T090 [US4] Update agent instructions to handle task update intents in phase-3/backend/agent/runner.py
- [X] T091 [US4] Test update_task tool invocation through OpenAI Agents SDK in phase-3/backend/agent/runner.py

**Checkpoint**: Users can now update task details via natural language

---

## Phase 8: User Story 5 - Delete Tasks (Priority: P5)

**Goal**: Users can remove tasks from their list through conversational commands.

**Independent Test**: Say "Delete buy groceries" or "Remove the call mom task" and verify the task is removed from the list.

### Function Tool Implementation

- [X] T092 [P] [US5] Create DeleteTaskInput Pydantic model in phase-3/backend/tools/delete_task.py
- [X] T093 [P] [US5] Implement delete_task function with @function_tool decorator in phase-3/backend/tools/delete_task.py
- [X] T094 [US5] Add user ownership verification in delete_task in phase-3/backend/tools/delete_task.py
- [X] T095 [US5] Add task not found error handling in delete_task in phase-3/backend/tools/delete_task.py
- [X] T096 [US5] Register delete_task tool with agent in phase-3/backend/agent/runner.py

### Agent Integration

- [X] T097 [US5] Update agent instructions to handle task deletion intents in phase-3/backend/agent/runner.py
- [X] T098 [US5] Add confirmation prompt for destructive operations in agent instructions in phase-3/backend/agent/runner.py
- [X] T099 [US5] Test delete_task tool invocation through OpenAI Agents SDK in phase-3/backend/agent/runner.py

**Checkpoint**: All user stories are now implemented - full CRUD operations via natural language

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Documentation

- [X] T100 [P] Create README.md in phase-3/ (setup instructions, architecture overview)
- [X] T101 [P] Update CLAUDE.md in phase-3/ (usage notes for Claude Code)
- [X] T102 [P] Document environment variables in phase-3/backend/.env.example and phase-3/frontend/.env.local.example

### Error Handling & Validation

- [X] T103 Add rate limiting for Groq API in phase-3/backend/agent/runner.py (handle 429 errors, implement backoff)
- [X] T104 Add input sanitization for XSS prevention in phase-3/backend/routes/chat.py (html.escape on user inputs)
- [ ] T105 Add conversation length limits in phase-3/backend/routes/chat.py (max messages per conversation)
- [X] T106 Add graceful degradation when Groq API unavailable in phase-3/backend/routes/chat.py (return helpful error message)

### Performance Optimization

- [X] T107 Add database query optimization in phase-3/backend/routes/chat.py (use select_related, limit queries)
- [ ] T108 Add response caching for common queries in phase-3/backend/agent/runner.py (cache "list all tasks" responses)
- [ ] T109 Optimize frontend bundle size in phase-3/frontend/ (code splitting, lazy loading)

### Security Hardening

- [ ] T110 Add HTTPS enforcement in phase-3/backend/main.py (redirect HTTP to HTTPS in production)
- [X] T111 Add request logging for audit trail in phase-3/backend/main.py (log all chat requests with user_id)
- [X] T112 Add secrets validation on startup in phase-3/backend/main.py (verify JWT_SECRET, GROQ_API_KEY are set)

### Testing & Validation

- [ ] T113 Run quickstart.md validation (follow setup guide, verify all steps work)
- [ ] T114 Test all user stories end-to-end (verify each acceptance scenario from spec.md)
- [ ] T115 Load test with 100 concurrent users (verify performance requirements met)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent of US1 but integrates naturally
- **User Story 6 (P2)**: Can start after Foundational (Phase 2) - Enhances all other stories but independent
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independent of other stories
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Independent of other stories
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - Independent of other stories

### Within Each User Story

- MCP tools can be implemented in parallel with agent runner intent recognition
- Chat endpoint depends on both MCP tools and agent runner being complete
- Frontend can be developed in parallel with backend (using mock data initially)
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1 (Setup)**: T002-T007 can all run in parallel (different files)
- **Phase 2 (Foundational)**: T012-T013 (auth), T014-T016 (MCP), T021-T024 (API) can run in parallel
- **Within User Stories**: MCP tool implementation and agent runner integration can run in parallel
- **Across User Stories**: Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)

---

## Parallel Example: User Story 1

```bash
# Launch MCP tool and agent runner tasks together:
Task T025: "Implement todo_create_task MCP tool in phase-3/backend/mcp/tools/add_task.py"
Task T029: "Add intent recognition for add task commands in phase-3/backend/agent/runner.py"

# Launch frontend tasks together:
Task T038: "Create ChatWindow component in phase-3/frontend/components/ChatWindow.tsx"
Task T039: "Create chat API client in phase-3/frontend/services/chatApi.ts"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T024) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T025-T045)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 6 → Test independently → Deploy/Demo (context awareness)
5. Add User Story 3 → Test independently → Deploy/Demo (complete tasks)
6. Add User Story 4 → Test independently → Deploy/Demo (update tasks)
7. Add User Story 5 → Test independently → Deploy/Demo (delete tasks)
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (T025-T045)
   - Developer B: User Story 2 (T046-T056)
   - Developer C: User Story 6 (T057-T068)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All file paths are relative to repository root
- OpenAI Agents SDK handles tool invocation automatically - no manual routing needed
- Function tools use @function_tool decorator with automatic schema generation from Pydantic models
- Groq accessed via LiteLLM integration for OpenAI SDK compatibility
- Follow contracts/tools-reference.md for complete tool implementation examples

## Task Summary

**Total Tasks**: 115

**Tasks by Phase**:
- Phase 1 (Setup): 7 tasks
- Phase 2 (Foundational): 17 tasks (includes OpenAI Agents SDK setup)
- Phase 3 (US1 - Add Tasks): 23 tasks
- Phase 4 (US2 - View Tasks): 11 tasks
- Phase 5 (US6 - Conversation Context): 15 tasks
- Phase 6 (US3 - Mark Complete): 9 tasks
- Phase 7 (US4 - Update Tasks): 9 tasks
- Phase 8 (US5 - Delete Tasks): 8 tasks
- Phase 9 (Polish): 16 tasks

**Parallel Opportunities**: 35+ tasks marked [P] can run in parallel within their phases

**MVP Scope**: Phase 1 + Phase 2 + Phase 3 = ~47 tasks for working MVP (add tasks via natural language)

**Independent Test Criteria**:
- US1: Send "Add buy groceries" → verify task created
- US2: Send "What's on my list?" → verify tasks displayed
- US3: Send "Mark buy groceries as done" → verify status updated
- US4: Send "Change buy groceries to organic groceries" → verify title updated
- US5: Send "Delete buy groceries" → verify task removed
- US6: Multi-turn conversation maintains context (foundational, tested across all stories)
