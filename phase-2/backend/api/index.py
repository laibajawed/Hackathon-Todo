"""
Vercel serverless function handler for FastAPI application.
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import from main
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app

# Export app directly for Vercel's ASGI support
# Vercel will automatically detect and handle the FastAPI app
__all__ = ['app']
