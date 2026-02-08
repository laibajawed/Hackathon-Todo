# Phase 2: Todo Full-Stack Web Application

A multi-user todo application with authentication, RESTful API, and responsive frontend.

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.13+)
- **Database**: Neon Serverless PostgreSQL
- **ORM**: SQLModel
- **Authentication**: JWT tokens with PyJWT
- **Password Hashing**: bcrypt

### Frontend
- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React hooks (useState, useEffect)

## Project Structure

```
phase-2/
├── backend/                 # FastAPI backend
│   ├── main.py             # Application entry point
│   ├── config.py           # Configuration settings
│   ├── database.py         # Database connection
│   ├── models.py           # SQLModel entities (User, Task)
│   ├── auth/               # Authentication module
│   │   ├── jwt.py          # JWT token handling
│   │   ├── dependencies.py # FastAPI dependencies
│   │   ├── schemas.py      # Pydantic schemas
│   │   └── utils.py        # Password hashing
│   ├── routes/             # API endpoints
│   │   ├── auth.py         # Authentication routes
│   │   └── tasks.py        # Task CRUD routes
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment variables template
│
└── frontend/               # Next.js frontend
    ├── app/                # Next.js App Router pages
    │   ├── layout.tsx      # Root layout with AuthProvider
    │   ├── page.tsx        # Landing page
    │   ├── auth/           # Authentication pages
    │   │   ├── signin/
    │   │   └── signup/
    │   └── tasks/          # Task management page
    ├── components/         # React components
    │   ├── AuthGuard.tsx   # Protected route wrapper
    │   ├── TaskList.tsx    # Task list display
    │   ├── TaskItem.tsx    # Individual task item
    │   └── TaskForm.tsx    # Task creation form
    ├── hooks/              # Custom React hooks
    │   ├── useAuth.ts      # Authentication state
    │   └── useTasks.ts     # Task data management
    ├── lib/                # Utility functions
    │   ├── api.ts          # API client
    │   └── types.ts        # TypeScript types
    └── .env.local.example  # Environment variables template

```

## Prerequisites

- **Python**: 3.13 or higher
- **Node.js**: 18 or higher
- **npm**: 9 or higher
- **Neon Account**: Sign up at https://neon.tech/

## Setup Instructions

### 1. Database Setup (Neon PostgreSQL)

1. Create a Neon project at https://console.neon.tech/
2. Copy your connection string
3. Replace `postgresql://` with `postgresql+asyncpg://` for async support

### 2. Backend Setup

```bash
# Navigate to backend directory
cd phase-2/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (WSL/Git Bash):
source venv/Scripts/activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env

# Edit .env with your values
# - DATABASE_URL: Your Neon connection string
# - JWT_SECRET: Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
nano .env

# Start the backend server
uvicorn main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000
API documentation: http://localhost:8000/docs

### 3. Frontend Setup

```bash
# Open a new terminal
# Navigate to frontend directory
cd phase-2/frontend

# Install dependencies
npm install

# Create .env.local file from example
cp .env.local.example .env.local

# Edit .env.local with your values
# - NEXT_PUBLIC_API_URL: http://localhost:8000
# - BETTER_AUTH_SECRET: Same value as JWT_SECRET in backend .env
nano .env.local

# Start the frontend server
npm run dev
```

Frontend will be available at: http://localhost:3000

## Environment Variables

### Backend (.env)

```bash
DATABASE_URL=postgresql+asyncpg://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
JWT_SECRET=your-super-secret-key-at-least-32-chars-long
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-super-secret-key-at-least-32-chars-long
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

**CRITICAL**: `BETTER_AUTH_SECRET` must match `JWT_SECRET` in backend `.env`

## Features

### User Authentication
- ✅ User registration with email and password
- ✅ User signin with JWT token generation
- ✅ Password hashing with bcrypt (cost factor 12)
- ✅ Protected routes requiring authentication

### Task Management
- ✅ Create tasks with title and optional description
- ✅ View all personal tasks (user isolation enforced)
- ✅ Mark tasks as complete/incomplete
- ✅ Edit task title and description
- ✅ Delete tasks with confirmation
- ✅ Task status indicators (pending/completed)

### Security
- ✅ JWT-based authentication
- ✅ User data isolation (users can only access their own tasks)
- ✅ XSS prevention via input sanitization
- ✅ CORS configuration for frontend-backend communication
- ✅ Secure password storage (bcrypt hashing)

### User Experience
- ✅ Responsive design (320px to 1920px)
- ✅ Loading states for async operations
- ✅ Error message display
- ✅ Empty state handling
- ✅ Optimistic UI updates
- ✅ Task statistics (total, completed)

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/signin` - Authenticate user

### Tasks (Protected)
- `GET /api/tasks` - List all user's tasks
- `POST /api/tasks` - Create new task
- `PUT /api/tasks/{id}` - Update task
- `PATCH /api/tasks/{id}/toggle` - Toggle task status
- `DELETE /api/tasks/{id}` - Delete task

## Development

### Backend Development

```bash
# Run with auto-reload
uvicorn main:app --reload --port 8000

# View API documentation
open http://localhost:8000/docs
```

### Frontend Development

```bash
# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## Troubleshooting

### Backend won't start - Database connection error
- Verify `DATABASE_URL` in `.env`
- Ensure using `postgresql+asyncpg://` prefix
- Check Neon database is active (not paused)

### Frontend can't connect to backend - CORS error
- Verify `CORS_ORIGINS` in backend `.env` includes `http://localhost:3000`
- Restart backend server after changing `.env`

### JWT token invalid
- Verify `JWT_SECRET` (backend) matches `BETTER_AUTH_SECRET` (frontend)
- Both must be identical strings
- Restart both servers after changing secrets
- Clear browser localStorage and sign in again

### Port already in use
```bash
# Find process using port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process or use different port
uvicorn main:app --reload --port 8001
npm run dev -- -p 3001
```

## Testing

### Manual Testing

1. **User Registration**: Create account at `/auth/signup`
2. **User Signin**: Sign in at `/auth/signin`
3. **Create Task**: Add new task on `/tasks` page
4. **View Tasks**: Verify tasks appear in list
5. **Toggle Status**: Mark task as complete/incomplete
6. **Edit Task**: Update task title and description
7. **Delete Task**: Remove task with confirmation
8. **User Isolation**: Create second account, verify tasks are separate

## Next Steps

- Phase 3: Chatbot Integration with MCP
- Phase 4: Event-Driven Architecture
- Phase 5: Cloud Deployment (Kubernetes)

## License

This project is part of a multi-phase todo application development series.
