# Implementation Plan: Todo AI Chatbot

**Branch**: `001-todo-ai-chatbot` | **Date**: 2026-01-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-todo-ai-chatbot/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build an AI-powered chatbot interface that enables users to manage their todo tasks through natural language conversation. The system will interpret user intent from conversational messages, invoke appropriate task operations via function tools, and maintain conversation context within user sessions. The chatbot integrates with existing Phase 2 authentication and task management infrastructure while adding conversational AI capabilities through OpenAI Agents SDK with Groq via LiteLLM (free LLM API).

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript/Next.js 16+ (frontend)
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, OpenAI Agents SDK with LiteLLM, Groq API (via LiteLLM), PyJWT, bcrypt
- Frontend: Next.js 16+ (App Router), React, Tailwind CSS, Better Auth
**Storage**: Neon Serverless PostgreSQL (existing from Phase 2, extended with Conversation and Message models)
**Testing**: pytest (backend), Jest/React Testing Library (frontend) - NEEDS CLARIFICATION: specific test coverage requirements
**Target Platform**: Web application (responsive design), WSL 2 compatible for development
**Project Type**: Web application (frontend + backend extending Phase 2 infrastructure)
**Performance Goals**:
- Message response time: <3 seconds for 95% of requests
- Support 100 concurrent users without degradation
- Conversation history queries: <1 second
**Constraints**:
- Session-based conversation history (cleared on logout)
- One active conversation per user at a time
- User isolation enforced via JWT validation
- Stateless chat endpoint and function tools
- Work limited to /phase-3 folder
**Scale/Scope**:
- 100 concurrent users initially
- 6 prioritized user stories (P1-P5)
- 5 function tools (create_task, update_task, delete_task, list_tasks, toggle_task_status)
- Single chat endpoint: POST /api/{user_id}/chat

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Initial Check (Before Phase 0) ✅ PASSED

All constitutional principles validated before research phase.

### I. Spec-First, Code-Second ✅
- **Status**: PASS
- **Evidence**: Complete specification exists at `specs/001-todo-ai-chatbot/spec.md` with 6 user stories, 16 functional requirements, and 8 success criteria
- **Next**: Proceeding to planning phase

### II. Zero Boilerplate ✅
- **Status**: PASS
- **Evidence**: All implementation will be generated via Claude Code agents following Spec-Kit Plus workflow
- **Constraint**: No manual coding permitted per user input constraints

### III. Deterministic Evolution ✅
- **Status**: PASS
- **Evidence**: This is Phase 3 (Chatbot Integration), building incrementally on Phase 2 (Web UI with FastAPI + Next.js + Neon PostgreSQL)
- **Foundation**: Reuses existing authentication (Better Auth + JWT), task CRUD operations, and database infrastructure
- **Next Phase**: Phase 4 (Event-Driven Architecture with Kafka/Dapr) explicitly out of scope

### IV. Agent-Native Design ✅
- **Status**: PASS
- **Evidence**: Tool-first architecture - Function tools expose task operations before UI layer
- **Implementation**: OpenAI Agents SDK with @function_tool decorator creates stateless tools that AI agent invokes for task operations
- **LLM Integration**: Groq via LiteLLM (free LLM API) enables AI assistant as first-class user

### Technology Stack Compliance ✅
- **Backend**: Python 3.13+ with FastAPI ✅
- **Data Layer**: SQLModel ORM on Neon PostgreSQL ✅
- **Frontend**: Next.js 16+ with React ✅
- **Runtime**: WSL 2 compatible ✅

### Authentication & Authorization ✅
- **Status**: PASS
- **Evidence**: JWT-based Better Auth enforces user isolation (FR-012, FR-013)
- **Implementation**: All chat requests validate JWT, conversation and message records linked to user_id
- **Multi-tenancy**: Strict tenant boundaries - users can only access their own tasks and conversations

### Development Workflow ✅
- **Status**: PASS
- **Evidence**: All implementation via Claude Code + Spec-Kit Plus (AI-assisted tools)
- **Constraint**: No manual coding per project constraints

**GATE RESULT**: ✅ ALL CHECKS PASS - Proceeding to Phase 0 Research

---

### Post-Design Check (After Phase 1) ✅ PASSED

**Re-validation Date**: 2026-01-23

#### I. Spec-First, Code-Second ✅
- **Status**: PASS
- **Evidence**: Complete design artifacts created before implementation:
  - research.md: Technology decisions documented
  - data-model.md: Database schema defined
  - contracts/chat-api.yaml: API contract specified
  - contracts/mcp-tools.json: MCP tool definitions
  - quickstart.md: Development guide
- **Validation**: No code written, only design artifacts

#### II. Zero Boilerplate ✅
- **Status**: PASS
- **Evidence**: All artifacts are specifications, not implementation
- **Next**: Implementation will be generated via Claude Code following `/sp.tasks`

#### III. Deterministic Evolution ✅
- **Status**: PASS
- **Evidence**: Design builds incrementally on Phase 2:
  - Extends existing FastAPI application
  - Reuses Phase 2 authentication (Better Auth + JWT)
  - Extends existing database with new tables
  - Reuses existing Task model for MCP tools
- **Validation**: No architectural leaps, clean extension of Phase 2

#### IV. Agent-Native Design ✅
- **Status**: PASS
- **Evidence**: Design maintains tool-first architecture with OpenAI Agents SDK
  - 5 function tools defined in contracts/tools-reference.md
  - Tools expose task operations before UI implementation
  - OpenAI Agents SDK with Groq invokes tools for natural language understanding
  - Stateless tool design with database as source of truth
- **Validation**: AI agent operates as first-class user via @function_tool decorated functions

#### Technology Stack Compliance ✅
- **Backend**: Python 3.13+ with FastAPI ✅
- **Data Layer**: SQLModel ORM on Neon PostgreSQL ✅
- **Frontend**: Next.js 16+ with React ✅
- **Runtime**: WSL 2 compatible ✅
- **New Additions**: OpenAI Agents SDK, LiteLLM, Groq API (all align with stack principles)

#### Authentication & Authorization ✅
- **Status**: PASS
- **Evidence**: Design enforces user isolation:
  - All MCP tools require user_id parameter
  - Ownership verification before operations
  - JWT validation on all chat endpoints
  - Conversation and Message tables linked to user_id
- **Validation**: Multi-tenancy enforced at data model and API level

#### Development Workflow ✅
- **Status**: PASS
- **Evidence**: AI-assisted development maintained:
  - All implementation via Claude Code + Spec-Kit Plus
  - No manual coding in design phase
  - Quickstart guide for AI-assisted setup
- **Validation**: Workflow follows constitutional requirements

**POST-DESIGN GATE RESULT**: ✅ ALL CHECKS PASS - Ready for Task Generation

**Design Quality Assessment**:
- All design artifacts complete and consistent
- No constitutional violations introduced
- Clean integration with Phase 2 infrastructure
- MCP-first architecture preserved
- Performance requirements validated (research.md)
- Security considerations documented (data-model.md)

**Recommendation**: Proceed to `/sp.tasks` for task breakdown

## Project Structure

### Documentation (this feature)

```text
specs/001-todo-ai-chatbot/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── chat-api.yaml    # OpenAPI spec for chat endpoint
│   └── mcp-tools.json   # MCP tool definitions
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
phase-3/
├── backend/
│   ├── models.py                    # Conversation, Message models (extends Phase 2)
│   ├── routes/
│   │   └── chat.py                  # POST /api/{user_id}/chat endpoint
│   ├── agent/
│   │   └── runner.py                # OpenAI Agents SDK integration with Groq via LiteLLM
│   ├── tools/
│   │   ├── __init__.py              # Export all function tools
│   │   ├── create_task.py           # @function_tool: create_task
│   │   ├── update_task.py           # @function_tool: update_task
│   │   ├── delete_task.py           # @function_tool: delete_task
│   │   ├── list_tasks.py            # @function_tool: list_tasks
│   │   └── toggle_task_status.py    # @function_tool: toggle_task_status
│   ├── tests/
│   │   ├── test_chat_api.py
│   │   ├── test_agent_runner.py
│   │   └── test_tools.py
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── app/
│   │   └── chat/
│   │       └── page.tsx             # Chat interface page
│   ├── components/
│   │   └── ChatWindow.tsx           # Chat UI component
│   ├── services/
│   │   └── chatApi.ts               # API client for chat endpoint
│   ├── tests/
│   │   └── ChatWindow.test.tsx
│   ├── package.json
│   └── .env.local.example
│
├── README.md                         # Setup instructions
└── CLAUDE.md                         # Claude Code usage notes
```

**Structure Decision**: Web application structure (Option 2) selected because feature requires both frontend chat UI and backend API/agent infrastructure. Phase 3 is organized as a standalone folder to maintain separation from Phase 1 (console) and Phase 2 (web) while enabling potential integration later. Backend extends Phase 2's FastAPI application with new chat endpoint, agent runner using OpenAI Agents SDK, and function tools with @function_tool decorator. Frontend extends Phase 2's Next.js application with new chat page and components.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitutional principles are satisfied.

---

## Phase 0: Research & Technology Decisions

*Status: PENDING - To be generated in research.md*

### Research Tasks

1. **OpenAI Agents SDK with Groq via LiteLLM**
   - Research: How to use OpenAI Agents SDK with LiteLLM for Groq integration
   - Research: Agent configuration and Runner patterns with Groq endpoint
   - Research: Conversation context management with OpenAI Agents SDK

2. **@function_tool Pattern Implementation**
   - Research: Function tool definition with @function_tool decorator
   - Research: Automatic schema generation from Pydantic models
   - Research: Tool invocation patterns and stateless tool design

3. **Conversation State Management**
   - Research: Session-based conversation storage patterns
   - Research: Conversation context passing to AI agent
   - Research: Efficient conversation history retrieval for context

4. **Natural Language Intent Recognition**
   - Research: Prompt engineering for task operation intent classification
   - Research: Handling ambiguous commands and clarification flows
   - Research: Context-aware pronoun resolution in multi-turn conversations

5. **Frontend Chat UI Options**
   - Research: Botpress open-source widget integration vs React Chat UI libraries
   - Decision needed: Which chat UI approach to use
   - Research: Real-time message streaming vs request-response pattern

6. **Integration with Phase 2 Infrastructure**
   - Research: Extending Phase 2 FastAPI app vs standalone service
   - Research: Reusing Phase 2 authentication middleware
   - Research: Database migration strategy for new Conversation/Message models

### Unknowns to Resolve

- **NEEDS CLARIFICATION**: Specific test coverage requirements (unit, integration, e2e percentages)
- **NEEDS CLARIFICATION**: Chat UI choice - Botpress widget or React Chat UI library (e.g., react-chat-elements, @chatscope/chat-ui-kit-react)
- **NEEDS CLARIFICATION**: Message streaming support - should responses stream in real-time or return complete?
- **NEEDS CLARIFICATION**: Conversation length limits - max messages per conversation?
- **NEEDS CLARIFICATION**: Error handling strategy when AI service unavailable - fallback behavior?

---

## Phase 1: Design Artifacts

*Status: PENDING - To be generated after Phase 0*

### Deliverables

1. **data-model.md**: Entity definitions for Conversation and Message models
2. **contracts/chat-api.yaml**: OpenAPI specification for POST /api/{user_id}/chat
3. **contracts/tools-reference.md**: Function tool definitions with @function_tool decorator patterns
4. **quickstart.md**: Development setup and testing guide

---

## Phase 2: Task Breakdown

*Status: PENDING - Generated by /sp.tasks command (NOT part of /sp.plan)*

Task generation will be handled by separate `/sp.tasks` command after plan approval.

---

## Architectural Decisions Requiring ADR

Based on the planning process, the following architecturally significant decisions should be documented:

1. **OpenAI Agents SDK for Agent Orchestration**
   - Decision: Use OpenAI Agents SDK instead of custom agent runner
   - Impact: Provides production-ready orchestration, automatic tool invocation, built-in conversation management
   - Alternatives: Custom agent runner with Groq SDK, LangChain, other agent frameworks

2. **Tool-First Architecture with @function_tool**
   - Decision: Expose all task operations via @function_tool decorated functions before implementing chat UI
   - Impact: Enables AI agent to operate as first-class user, aligns with Agent-Native Design principle
   - Alternatives: Direct database access from agent, REST API calls from agent, MCP server architecture

3. **Groq via LiteLLM for LLM Inference**
   - Decision: Use Groq Cloud API via LiteLLM integration for fast, cost-effective LLM inference
   - Impact: Provides free access to high-performance LLMs (Llama models) with tool calling support, maintains OpenAI SDK compatibility
   - Alternatives: OpenAI API (paid), Anthropic API (paid), local LLM (complex setup), direct Groq SDK

4. **Session-Based Conversation Storage**
   - Decision: Store conversation history only for session duration, clear on logout
   - Impact: Simplifies storage requirements, reduces privacy concerns, limits context window
   - Alternatives: 30-day retention, indefinite retention, no persistence

**Recommendation**: Run `/sp.adr` for each decision after plan approval to document reasoning and tradeoffs.

---

## Next Steps

1. **Phase 0 Execution**: Generate `research.md` by dispatching research agents for each unknown
2. **Phase 1 Execution**: Generate design artifacts (data-model.md, contracts/, quickstart.md)
3. **Agent Context Update**: Run `.specify/scripts/bash/update-agent-context.sh claude`
4. **Constitution Re-check**: Validate design artifacts against constitutional principles
5. **Task Generation**: User runs `/sp.tasks` to break down implementation into actionable tasks
6. **ADR Creation**: User runs `/sp.adr <decision-title>` for each architectural decision

**Current Status**: Plan complete, ready for Phase 0 research execution.
