"""
Vercel serverless function handler for FastAPI application.
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import from main
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app

# Vercel expects 'app' or 'handler'
handler = app
