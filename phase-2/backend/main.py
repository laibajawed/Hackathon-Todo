"""
Main FastAPI application.
Configures CORS, routes, and application lifecycle events.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from middleware import SecurityHeadersMiddleware

# Create FastAPI application
app = FastAPI(
    title="Todo API",
    description="RESTful API for multi-user todo application with JWT authentication",
    version="1.0.0"
)

# Note: Database initialization removed for serverless compatibility
# Tables should be created via migration scripts or manual setup
# Startup events don't work in Vercel's serverless environment

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

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


@app.get("/health")
async def health_check():
    """
    Health check endpoint with database connectivity verification.
    Returns 200 if healthy, 503 if database is unreachable.
    """
    from database import get_engine
    from sqlalchemy import text

    try:
        # Test database connection
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected",
            "version": "1.0.0"
        }
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )


# Import and include routers
from routes import auth, tasks
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
