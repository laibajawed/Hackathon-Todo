"""
Database initialization script for serverless deployment.
Run this script once to create all database tables.

Usage:
    python init_db.py
"""
import asyncio
from database import init_db


async def main():
    """Initialize database tables."""
    print("Initializing database tables...")
    try:
        await init_db()
        print("✓ Database tables created successfully!")
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
