"""
Main FastAPI application.
Configures CORS, routes, and application lifecycle events.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
from config import settings
from database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup: Initialize database
    await init_db()
    print("✓ Database initialized")

    # Note: MCP server runs as subprocess (spawned by agent runner), not mounted here
    print("✓ MCP server will be spawned per-request by agent runner")

    yield
    # Shutdown: Cleanup if needed
    print("✓ Application shutdown")


# Create FastAPI application
app = FastAPI(
    title="Todo API",
    description="RESTful API for multi-user todo application with JWT authentication",
    version="1.0.0",
    lifespan=lifespan
)

# HTTPS enforcement middleware (production only)
@app.middleware("http")
async def https_redirect_middleware(request: Request, call_next):
    """
    Redirect HTTP to HTTPS in production.
    Only enforces HTTPS when ENVIRONMENT is set to 'production'.
    """
    if settings.ENVIRONMENT == "production":
        # Check if request is HTTP (not HTTPS)
        if request.url.scheme == "http":
            # Redirect to HTTPS
            https_url = request.url.replace(scheme="https")
            return RedirectResponse(url=str(https_url), status_code=301)

    # Continue with request
    response = await call_next(request)
    return response

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Todo API is running",
        "version": "1.0.0"
    }


# Import and include routers
from routes import auth, tasks, chat
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
