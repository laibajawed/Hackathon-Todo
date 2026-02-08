#!/usr/bin/env python3
"""Debug server subprocess stderr."""
import os
import sys
import asyncio
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

async def debug_server():
    """Run server and capture all output."""
    backend_dir = Path(__file__).parent
    mcp_server_path = backend_dir / "mcp_server" / "server.py"
    
    database_url = os.getenv("DATABASE_URL")
    
    env = {
        **os.environ,
        "USER_ID": "test-user-123",
        "DATABASE_URL": database_url,
        "PYTHONPATH": str(backend_dir),
    }
    
    print("Starting server subprocess...", file=sys.stderr)
    
    proc = subprocess.Popen(
        [sys.executable, str(mcp_server_path)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )
    
    # Wait for startup
    await asyncio.sleep(3)
    
    # Check if still running
    if proc.poll() is None:
        print("✓ Server is running", file=sys.stderr)
        
        # Send a test message to stdin
        try:
            proc.stdin.write(b'{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}\n')
            proc.stdin.flush()
            print("✓ Sent initialize message", file=sys.stderr)
        except Exception as e:
            print(f"✗ Failed to send message: {e}", file=sys.stderr)
        
        # Wait a bit more
        await asyncio.sleep(2)
        
        # Try to read stderr
        proc.terminate()
        try:
            stdout, stderr = proc.communicate(timeout=2)
            print(f"\n=== STDOUT ===\n{stdout.decode()}", file=sys.stderr)
            print(f"\n=== STDERR ===\n{stderr.decode()}", file=sys.stderr)
        except:
            print("Could not read output", file=sys.stderr)
    else:
        print(f"✗ Server exited with code: {proc.returncode}", file=sys.stderr)
        stdout, stderr = proc.communicate()
        print(f"\n=== STDOUT ===\n{stdout.decode()}", file=sys.stderr)
        print(f"\n=== STDERR ===\n{stderr.decode()}", file=sys.stderr)

if __name__ == "__main__":
    asyncio.run(debug_server())
