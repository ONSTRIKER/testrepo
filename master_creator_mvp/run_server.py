"""
Master Creator MVP - Server Launcher
Starts the FastAPI server with correct Python paths
"""

import sys
import os
from pathlib import Path

# Load environment variables from .env file FIRST
from dotenv import load_dotenv
load_dotenv()

# Add current directory to Python path so 'src' module can be found
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Set environment variable for PYTHONPATH as well
os.environ['PYTHONPATH'] = str(current_dir)

print("=" * 60)
print("Master Creator MVP - Starting Server")
print("=" * 60)
print(f"Python path: {current_dir}")
print(f"Python version: {sys.version}")
print()

# Import and run uvicorn
import uvicorn

print("Starting FastAPI server...")
print("Server will be available at: http://localhost:8080")
print("API Documentation: http://localhost:8080/api/docs")
print()
print("Press Ctrl+C to stop the server")
print("=" * 60)
print()

# Run the server
uvicorn.run(
    "src.api.main:app",
    host="0.0.0.0",
    port=8080,
    reload=False,  # Disable reload on Windows for stability
    log_level="info",
)
