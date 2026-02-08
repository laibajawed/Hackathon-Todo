# Quickstart Guide: Todo AI Chatbot

**Feature**: 001-todo-ai-chatbot
**Date**: 2026-01-23
**Audience**: Developers setting up the chatbot for development and testing

## Overview

This guide walks you through setting up the Todo AI Chatbot feature from scratch, including backend API, MCP server, agent runner, and frontend chat UI.

**Prerequisites:**
- Phase 2 infrastructure running (FastAPI backend + Next.js frontend)
- Python 3.13+ installed
- Node.js 18+ installed
- PostgreSQL database (Neon) accessible
- Groq API account (free tier for development)

**Estimated Setup Time**: 30-45 minutes

---

## Table of Contents

1. [Environment Setup](#1-environment-setup)
2. [Database Migration](#2-database-migration)
3. [Backend Setup](#3-backend-setup)
4. [Frontend Setup](#4-frontend-setup)
5. [Testing](#5-testing)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. Environment Setup

### 1.1 Get Groq API Key

1. Visit https://console.groq.com/home
2. Sign up for a free account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (you won't see it again)

### 1.2 Configure Environment Variables

**Backend (.env):**

```bash
# Navigate to backend directory
cd phase-3/backend

# Create .env file
cat > .env << 'EOF'
# Database (reuse from Phase 2)
DATABASE_URL=postgresql://user:password@host/database

# Authentication (reuse from Phase 2)
JWT_SECRET=your-jwt-secret-from-phase-2

# Groq API
GROQ_API_KEY=your-groq-api-key-here

# Optional: Groq Configuration
GROQ_MODEL=llama-3.1-8b-instant
GROQ_MAX_TOKENS=1000
GROQ_TEMPERATURE=0.7

# Optional: Rate Limiting
RATE_LIMIT_RPM=30  # Free tier: 30 requests per minute
RATE_LIMIT_TPM=6000  # Free tier: 6000 tokens per minute
EOF
```

**Frontend (.env.local):**

```bash
# Navigate to frontend directory
cd phase-3/frontend

# Create .env.local file
cat > .env.local << 'EOF'
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Authentication (reuse from Phase 2)
BETTER_AUTH_SECRET=your-better-auth-secret-from-phase-2
BETTER_AUTH_URL=http://localhost:3000
EOF
```

### 1.3 Install Dependencies

**Backend:**

```bash
cd phase-3/backend

# Install Python dependencies
pip install -r requirements.txt

# Or with uv (recommended)
uv pip install -r requirements.txt
```

**requirements.txt:**
```
fastapi>=0.100.0
sqlmodel>=0.0.14
groq>=0.4.0
pydantic>=2.0.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
uvicorn[standard]>=0.23.0
alembic>=1.12.0
psycopg2-binary>=2.9.9
tiktoken>=0.5.0
mcp>=0.1.0
httpx>=0.25.0
```

**Frontend:**

```bash
cd phase-3/frontend

# Install Node dependencies
npm install
```

---

## 2. Database Migration

### 2.1 Create Migration

```bash
cd phase-3/backend

# Generate migration for conversation tables
alembic revision --autogenerate -m "Add conversation and message tables"

# Review the generated migration in alembic/versions/
# Ensure it includes:
# - conversations table with indexes
# - messages table with indexes
# - Foreign key constraints with CASCADE
```

### 2.2 Run Migration

```bash
# Apply migration
alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt"
# Should show: conversations, messages tables

# Verify indexes
psql $DATABASE_URL -c "\di"
# Should show: idx_user_active, idx_conversation_sequence, idx_conversation_created
```

### 2.3 Rollback (if needed)

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>
```

---

## 3. Backend Setup

### 3.1 Project Structure

Ensure your backend has this structure:

```
phase-3/backend/
├── models.py              # Conversation, Message models
├── routes/
│   └── chat.py            # Chat endpoint
├── agent/
│   └── runner.py          # Groq agent runner
├── mcp/
│   ├── server.py          # MCP server
│   └── tools/
│       ├── __init__.py
│       ├── add_task.py
│       ├── update_task.py
│       ├── delete_task.py
│       ├── list_tasks.py
│       └── complete_task.py
├── database.py            # Database connection
├── auth.py                # JWT middleware
├── main.py                # FastAPI app
├── requirements.txt
└── .env
```

### 3.2 Start Backend Server

```bash
cd phase-3/backend

# Start with uvicorn
uvicorn main:app --reload --port 8000

# Or with hot reload
uvicorn main:app --reload --port 8000 --log-level debug
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 3.3 Verify Backend

**Health Check:**
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

**API Documentation:**
```bash
# Open in browser
open http://localhost:8000/docs
# Should show Swagger UI with chat endpoints
```

---

## 4. Frontend Setup

### 4.1 Start Frontend Server

```bash
cd phase-3/frontend

# Start Next.js dev server
npm run dev
```

**Expected Output:**
```
  ▲ Next.js 16.0.0
  - Local:        http://localhost:3000
  - Ready in 2.3s
```

### 4.2 Verify Frontend

**Open Chat Interface:**
```bash
# Open in browser
open http://localhost:3000/chat
```

**Expected:**
- Login page if not authenticated
- Chat interface with empty state message if authenticated
- "Welcome to Todo Chat!" message

---

## 5. Testing

### 5.1 Manual Testing Flow

**Step 1: Authenticate**
```bash
# Login via UI or get JWT token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# Save the token
export TOKEN="your-jwt-token-here"
```

**Step 2: Send Chat Message**
```bash
# Create a task via chat
curl -X POST http://localhost:8000/api/123e4567-e89b-12d3-a456-426614174000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message": "Add a task to buy groceries"}'

# Expected response:
# {
#   "response": "I've added 'buy groceries' to your todo list.",
#   "conversation_id": 1,
#   "tokens_used": 156,
#   "tool_calls": [...]
# }
```

**Step 3: List Tasks**
```bash
curl -X POST http://localhost:8000/api/123e4567-e89b-12d3-a456-426614174000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message": "Show me my tasks"}'
```

**Step 4: Complete Task**
```bash
curl -X POST http://localhost:8000/api/123e4567-e89b-12d3-a456-426614174000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message": "Mark the grocery task as done"}'
```

**Step 5: Get Conversation History**
```bash
curl -X GET http://localhost:8000/api/123e4567-e89b-12d3-a456-426614174000/chat/history \
  -H "Authorization: Bearer $TOKEN"
```

### 5.2 Automated Testing

**Backend Unit Tests:**
```bash
cd phase-3/backend

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_chat_api.py -v
```

**Frontend Tests:**
```bash
cd phase-3/frontend

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test
npm test -- ChatWindow.test.tsx
```

### 5.3 Integration Testing

**End-to-End Flow:**
```bash
# Run E2E test script
cd phase-3
./scripts/test-e2e.sh

# Or manually:
# 1. Start backend
# 2. Start frontend
# 3. Run Playwright tests
npm run test:e2e
```

### 5.4 Performance Testing

**Load Test with Apache Bench:**
```bash
# Test chat endpoint with 100 concurrent requests
ab -n 1000 -c 100 -T application/json \
  -H "Authorization: Bearer $TOKEN" \
  -p message.json \
  http://localhost:8000/api/123e4567-e89b-12d3-a456-426614174000/chat

# message.json:
# {"message": "Show me my tasks"}
```

**Expected Results:**
- 95th percentile: <3 seconds
- Success rate: >99%
- No 429 errors (rate limiting) with free tier

---

## 6. Troubleshooting

### 6.1 Common Issues

**Issue: "Groq API rate limit exceeded"**

**Symptoms:**
```json
{
  "error": true,
  "message": "Rate limit exceeded. Please try again in 60 seconds.",
  "code": "RATE_LIMIT_EXCEEDED"
}
```

**Solution:**
- Free tier: 30 RPM limit
- Wait 60 seconds between requests
- Upgrade to Developer plan for production
- Implement client-side rate limiting

---

**Issue: "Database connection error"**

**Symptoms:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**
```bash
# Check DATABASE_URL is correct
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"

# Check Neon database is running
# Visit https://console.neon.tech

# Verify connection pool settings
# In database.py, check pool_size and max_overflow
```

---

**Issue: "JWT token invalid or expired"**

**Symptoms:**
```json
{
  "error": true,
  "message": "Invalid or expired authentication token",
  "code": "UNAUTHORIZED"
}
```

**Solution:**
```bash
# Get new token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# Verify JWT_SECRET matches between Phase 2 and Phase 3
grep JWT_SECRET phase-2/backend/.env
grep JWT_SECRET phase-3/backend/.env
```

---

**Issue: "MCP tool not found"**

**Symptoms:**
```json
{
  "error": true,
  "message": "Unknown tool: todo_create_task"
}
```

**Solution:**
```bash
# Verify MCP server is running
ps aux | grep mcp_server

# Check tool registration
python -c "from mcp_server import mcp; print(mcp.list_tools())"

# Restart backend server
pkill -f uvicorn
uvicorn main:app --reload --port 8000
```

---

**Issue: "Conversation not found"**

**Symptoms:**
```json
{
  "error": true,
  "message": "No active conversation found for this user",
  "code": "NOT_FOUND"
}
```

**Solution:**
- Conversation is created on first message
- Send a message to initialize conversation
- Check database for conversations:
```sql
SELECT * FROM conversations WHERE user_id = 123;
```

---

**Issue: "Frontend can't connect to backend"**

**Symptoms:**
- Network error in browser console
- CORS errors

**Solution:**
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check NEXT_PUBLIC_API_URL
grep NEXT_PUBLIC_API_URL phase-3/frontend/.env.local

# Verify CORS settings in backend
# In main.py, check CORSMiddleware configuration
```

---

### 6.2 Debug Mode

**Enable Debug Logging:**

**Backend:**
```python
# In main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Frontend:**
```bash
# Set debug environment variable
export DEBUG=true
npm run dev
```

**Groq API:**
```python
# In agent/runner.py
import httpx
httpx_client = httpx.AsyncClient(timeout=30.0, verify=True)
# Add logging for requests/responses
```

---

### 6.3 Monitoring

**Check Logs:**
```bash
# Backend logs
tail -f logs/backend.log

# Frontend logs
tail -f .next/trace

# Database logs (Neon)
# Visit https://console.neon.tech → Monitoring
```

**Monitor Performance:**
```bash
# Watch response times
watch -n 1 'curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health'

# curl-format.txt:
# time_total: %{time_total}s
```

---

## 7. Development Workflow

### 7.1 Making Changes

**Backend Changes:**
```bash
# 1. Make code changes
# 2. Server auto-reloads (uvicorn --reload)
# 3. Test changes
curl -X POST http://localhost:8000/api/.../chat ...

# 4. Run tests
pytest tests/test_chat_api.py
```

**Frontend Changes:**
```bash
# 1. Make code changes
# 2. Next.js auto-reloads
# 3. Test in browser
open http://localhost:3000/chat

# 4. Run tests
npm test -- ChatWindow.test.tsx
```

**Database Changes:**
```bash
# 1. Modify models in models.py
# 2. Generate migration
alembic revision --autogenerate -m "Description"

# 3. Review migration
cat alembic/versions/xxx_description.py

# 4. Apply migration
alembic upgrade head
```

### 7.2 Code Quality

**Linting:**
```bash
# Backend
cd phase-3/backend
ruff check .
black --check .

# Frontend
cd phase-3/frontend
npm run lint
```

**Type Checking:**
```bash
# Backend
mypy .

# Frontend
npm run type-check
```

---

## 8. Production Deployment

### 8.1 Pre-Deployment Checklist

- [ ] Upgrade to Groq Developer plan (1,000 RPM)
- [ ] Set production DATABASE_URL
- [ ] Generate strong JWT_SECRET
- [ ] Enable HTTPS/TLS
- [ ] Configure CORS for production domain
- [ ] Set up monitoring and alerting
- [ ] Run full test suite
- [ ] Load test with expected traffic
- [ ] Review security settings

### 8.2 Environment Variables (Production)

```bash
# Backend
DATABASE_URL=postgresql://prod-user:prod-pass@prod-host/prod-db
JWT_SECRET=<strong-random-secret>
GROQ_API_KEY=<production-api-key>
GROQ_MODEL=llama-3.1-8b-instant
RATE_LIMIT_RPM=1000  # Developer plan
RATE_LIMIT_TPM=250000  # Developer plan
ENVIRONMENT=production

# Frontend
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
BETTER_AUTH_SECRET=<strong-random-secret>
BETTER_AUTH_URL=https://yourdomain.com
```

---

## 9. Quick Reference

### 9.1 Useful Commands

```bash
# Start everything
cd phase-3
./scripts/start-all.sh

# Stop everything
./scripts/stop-all.sh

# Reset database
alembic downgrade base
alembic upgrade head

# Clear conversation data
psql $DATABASE_URL -c "TRUNCATE conversations CASCADE"

# Check Groq API status
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer $GROQ_API_KEY"
```

### 9.2 Key URLs

- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:3000
- Chat Interface: http://localhost:3000/chat
- Groq Console: https://console.groq.com
- Neon Console: https://console.neon.tech

---

## 10. Next Steps

After completing setup:

1. **Run `/sp.tasks`** to generate implementation tasks
2. **Review ADR recommendations** in plan.md
3. **Start implementation** following task breakdown
4. **Test incrementally** as you build
5. **Document issues** in GitHub issues

---

## Support

**Documentation:**
- Spec: `specs/001-todo-ai-chatbot/spec.md`
- Plan: `specs/001-todo-ai-chatbot/plan.md`
- Research: `specs/001-todo-ai-chatbot/research.md`
- Data Model: `specs/001-todo-ai-chatbot/data-model.md`

**External Resources:**
- Groq Docs: https://console.groq.com/docs
- FastMCP Docs: https://github.com/anthropics/mcp
- FastAPI Docs: https://fastapi.tiangolo.com
- Next.js Docs: https://nextjs.org/docs

**Getting Help:**
- Check troubleshooting section above
- Review error logs
- Search GitHub issues
- Ask in project chat
