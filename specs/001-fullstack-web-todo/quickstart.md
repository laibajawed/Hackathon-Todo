# Quickstart Guide

**Feature**: Todo Full-Stack Web Application (Basic Level)
**Date**: 2026-01-13
**Status**: Final

## Overview

This guide will help you set up and run the Phase 2 Todo Full-Stack Web Application locally. The application consists of a FastAPI backend, Next.js frontend, and Neon PostgreSQL database.

**Estimated Setup Time**: 15-20 minutes

---

## Prerequisites

Before you begin, ensure you have the following installed:

### Required Software

| Software | Minimum Version | Check Command | Installation |
|----------|----------------|---------------|--------------|
| Python | 3.13+ | `python --version` | https://www.python.org/downloads/ |
| Node.js | 18+ | `node --version` | https://nodejs.org/ |
| npm | 9+ | `npm --version` | Included with Node.js |
| Git | 2.0+ | `git --version` | https://git-scm.com/ |

### Required Accounts

- **Neon Account**: Sign up at https://neon.tech/ (free tier available)

### System Requirements

- **OS**: Windows (WSL 2), macOS, or Linux
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 500MB for dependencies

---

## Step 1: Clone the Repository

```bash
# Clone the repository
git clone <repository-url>
cd <repository-name>

# Checkout the Phase 2 branch
git checkout 001-fullstack-web-todo

# Navigate to Phase 2 directory
cd phase-2
```

---

## Step 2: Set Up Neon PostgreSQL Database

### 2.1 Create Neon Project

1. Go to https://console.neon.tech/
2. Click "Create Project"
3. Choose a project name (e.g., "todo-app-phase2")
4. Select a region (choose closest to your location)
5. Click "Create Project"

### 2.2 Get Connection String

1. In your Neon project dashboard, click "Connection Details"
2. Copy the connection string (it looks like this):
   ```
   postgresql://user:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require
   ```
3. **Important**: Replace `postgresql://` with `postgresql+asyncpg://` for async support:
   ```
   postgresql+asyncpg://user:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require
   ```

### 2.3 Verify Connection (Optional)

```bash
# Install psql client (if not already installed)
# On Ubuntu/Debian: sudo apt-get install postgresql-client
# On macOS: brew install postgresql

# Test connection
psql "postgresql://user:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require"

# If successful, you'll see:
# psql (15.x)
# SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, bits: 256, compression: off)
# Type "help" for help.
# dbname=>

# Exit with: \q
```

---

## Step 3: Set Up Backend (FastAPI)

### 3.1 Navigate to Backend Directory

```bash
cd phase-2/backend
```

### 3.2 Create Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (WSL/Git Bash):
source venv/Scripts/activate

# On macOS/Linux:
source venv/bin/activate

# Verify activation (you should see (venv) in your prompt)
which python  # Should point to venv/bin/python
```

### 3.3 Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Expected packages:
# - fastapi
# - uvicorn[standard]
# - sqlmodel
# - asyncpg
# - pyjwt
# - bcrypt
# - python-dotenv
# - pydantic[email]
```

### 3.4 Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your values
nano .env  # or use your preferred editor
```

**Required Environment Variables** (`.env`):

```bash
# Database connection (from Step 2.2)
DATABASE_URL=postgresql+asyncpg://user:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require

# JWT secret (generate a secure random string)
# You can generate one with: python -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_SECRET=your-super-secret-key-at-least-32-chars-long

# Environment
ENVIRONMENT=development

# CORS origins (frontend URL)
CORS_ORIGINS=http://localhost:3000
```

### 3.5 Initialize Database

```bash
# Run database migrations (creates tables)
alembic upgrade head

# Or if using SQLModel directly:
python -c "from database import init_db; import asyncio; asyncio.run(init_db())"
```

### 3.6 Start Backend Server

```bash
# Start FastAPI server with hot reload
uvicorn main:app --reload --port 8000

# Expected output:
# INFO:     Will watch for changes in these directories: ['/path/to/backend']
# INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process [xxxxx] using StatReload
# INFO:     Started server process [xxxxx]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
```

### 3.7 Verify Backend

Open a new terminal and test the API:

```bash
# Health check (if implemented)
curl http://localhost:8000/

# Or visit in browser:
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

**Keep this terminal running** - the backend server needs to stay active.

---

## Step 4: Set Up Frontend (Next.js)

### 4.1 Open New Terminal

Open a **new terminal window/tab** (keep backend running in the first terminal).

```bash
# Navigate to frontend directory
cd phase-2/frontend
```

### 4.2 Install Dependencies

```bash
# Install Node.js dependencies
npm install

# Expected packages:
# - next
# - react
# - react-dom
# - better-auth
# - tailwindcss
# - typescript
# - @types/react
# - @types/node
```

### 4.3 Configure Environment Variables

```bash
# Copy example environment file
cp .env.local.example .env.local

# Edit .env.local with your values
nano .env.local  # or use your preferred editor
```

**Required Environment Variables** (`.env.local`):

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth secret (MUST match backend JWT_SECRET)
BETTER_AUTH_SECRET=your-super-secret-key-at-least-32-chars-long

# Next.js URL (for Better Auth callbacks)
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

**CRITICAL**: `BETTER_AUTH_SECRET` must be **identical** to `JWT_SECRET` in backend `.env`

### 4.4 Start Frontend Server

```bash
# Start Next.js development server
npm run dev

# Expected output:
#   ▲ Next.js 16.x
#   - Local:        http://localhost:3000
#   - Environments: .env.local
#
#  ✓ Ready in 2.5s
```

### 4.5 Verify Frontend

Open your browser and navigate to:

```
http://localhost:3000
```

You should see the landing page of the Todo application.

**Keep this terminal running** - the frontend server needs to stay active.

---

## Step 5: First-Time User Flow

Now that both servers are running, let's walk through the complete user flow.

### 5.1 Register a New Account

1. Navigate to http://localhost:3000
2. Click "Sign Up" or navigate to http://localhost:3000/auth/signup
3. Enter your email and password:
   - Email: `test@example.com`
   - Password: `TestPassword123!` (min 8 characters)
4. Click "Sign Up"
5. You should be automatically logged in and redirected to `/tasks`

### 5.2 Create Your First Task

1. On the tasks page, you should see an empty state (no tasks yet)
2. Click "Add Task" or find the task creation form
3. Enter task details:
   - Title: `Complete Phase 2 setup`
   - Description: `Successfully set up and run the application`
4. Click "Create" or "Save"
5. Your task should appear in the task list with "pending" status

### 5.3 Manage Tasks

**Mark as Complete**:
- Click the checkbox or "Complete" button next to your task
- Status should change to "completed"
- Visual indicator should update (e.g., strikethrough, checkmark)

**Edit Task**:
- Click "Edit" button on your task
- Modify title or description
- Click "Save"
- Changes should be reflected immediately

**Delete Task**:
- Click "Delete" button on your task
- Confirm deletion (if prompted)
- Task should be removed from the list

### 5.4 Test User Isolation

1. Open a new incognito/private browser window
2. Navigate to http://localhost:3000
3. Sign up with a different email: `test2@example.com`
4. Create a task in this account
5. Verify that you **cannot** see tasks from the first account
6. Switch back to the first browser window
7. Verify that you **cannot** see tasks from the second account

**Expected Result**: Each user only sees their own tasks (user isolation working correctly).

---

## Step 6: Verify API Endpoints

You can test the API directly using curl or tools like Postman.

### 6.1 Sign Up via API

```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "api-test@example.com",
    "password": "ApiTest123!"
  }'

# Expected response:
# {
#   "user": {
#     "id": "...",
#     "email": "api-test@example.com",
#     "created_at": "..."
#   },
#   "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
# }
```

### 6.2 Create Task via API

```bash
# Save the token from signup response
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Create a task
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "API Test Task",
    "description": "Created via curl"
  }'

# Expected response:
# {
#   "id": "...",
#   "user_id": "...",
#   "title": "API Test Task",
#   "description": "Created via curl",
#   "status": "pending",
#   "created_at": "...",
#   "updated_at": "..."
# }
```

### 6.3 List Tasks via API

```bash
curl -X GET http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN"

# Expected response:
# [
#   {
#     "id": "...",
#     "title": "API Test Task",
#     ...
#   }
# ]
```

---

## Common Issues & Troubleshooting

### Issue 1: Backend Won't Start - Database Connection Error

**Symptom**:
```
sqlalchemy.exc.OperationalError: (asyncpg.exceptions.InvalidPasswordError)
```

**Solution**:
1. Verify your `DATABASE_URL` in `backend/.env`
2. Ensure you're using `postgresql+asyncpg://` (not just `postgresql://`)
3. Check that your Neon database is active (not paused)
4. Verify credentials are correct in Neon console

### Issue 2: Frontend Can't Connect to Backend - CORS Error

**Symptom** (in browser console):
```
Access to fetch at 'http://localhost:8000/api/tasks' from origin 'http://localhost:3000'
has been blocked by CORS policy
```

**Solution**:
1. Verify `CORS_ORIGINS` in `backend/.env` includes `http://localhost:3000`
2. Restart backend server after changing `.env`
3. Clear browser cache and reload

### Issue 3: JWT Token Invalid

**Symptom**:
```
401 Unauthorized: Invalid token
```

**Solution**:
1. Verify `JWT_SECRET` in `backend/.env` matches `BETTER_AUTH_SECRET` in `frontend/.env.local`
2. Both must be **identical** strings
3. Restart both servers after changing secrets
4. Clear browser cookies and sign in again

### Issue 4: Port Already in Use

**Symptom**:
```
Error: listen EADDRINUSE: address already in use :::8000
```

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Or use different ports:
# Backend: uvicorn main:app --reload --port 8001
# Frontend: npm run dev -- -p 3001
```

### Issue 5: Module Not Found Errors

**Symptom**:
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep fastapi
```

### Issue 6: Next.js Build Errors

**Symptom**:
```
Error: Cannot find module 'next'
```

**Solution**:
```bash
# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall dependencies
npm install

# Clear Next.js cache
rm -rf .next
```

---

## Development Workflow

### Daily Startup

```bash
# Terminal 1: Backend
cd phase-2/backend
source venv/bin/activate
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd phase-2/frontend
npm run dev
```

### Stopping Servers

```bash
# In each terminal, press:
Ctrl + C

# Deactivate Python virtual environment (backend terminal):
deactivate
```

### Making Changes

**Backend Changes**:
- Edit Python files in `backend/`
- Server auto-reloads (thanks to `--reload` flag)
- Check terminal for errors

**Frontend Changes**:
- Edit TypeScript/React files in `frontend/`
- Next.js Fast Refresh updates browser automatically
- Check browser console for errors

**Database Schema Changes**:
```bash
# Create migration
alembic revision --autogenerate -m "Description of changes"

# Apply migration
alembic upgrade head
```

---

## Next Steps

After completing this quickstart:

1. **Explore the API**: Visit http://localhost:8000/docs for interactive API documentation
2. **Review the Code**: Familiarize yourself with the project structure
3. **Run Tests**: Execute test suites (when implemented)
4. **Read Documentation**: Check `specs/001-fullstack-web-todo/` for detailed specs

---

## Useful Commands

### Backend

```bash
# Run tests
pytest

# Check code style
black . --check
flake8 .

# Database migrations
alembic revision --autogenerate -m "message"
alembic upgrade head
alembic downgrade -1

# Start production server
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
# Run tests
npm test

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint

# Type check
npm run type-check
```

---

## Getting Help

If you encounter issues not covered in this guide:

1. **Check Logs**: Review terminal output for error messages
2. **Browser Console**: Check for JavaScript errors (F12 → Console)
3. **API Documentation**: Visit http://localhost:8000/docs
4. **Project Documentation**: Review files in `specs/001-fullstack-web-todo/`
5. **GitHub Issues**: Search or create an issue in the repository

---

## Summary

You should now have:

- ✅ Neon PostgreSQL database provisioned and connected
- ✅ FastAPI backend running on http://localhost:8000
- ✅ Next.js frontend running on http://localhost:3000
- ✅ User registration and authentication working
- ✅ Task CRUD operations functional
- ✅ User isolation verified

**Congratulations!** You've successfully set up the Phase 2 Todo Full-Stack Web Application.

---

**Quickstart Guide Status**: ✅ COMPLETE
**Date Completed**: 2026-01-13
**Last Updated**: 2026-01-13
