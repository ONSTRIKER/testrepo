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

# DEBUG: Show what DATABASE_URL is loaded
database_url = os.getenv("DATABASE_URL", "NOT SET")
print(f"DATABASE_URL: {database_url}")
if database_url.startswith("postgresql"):
    print()
    print("!" * 60)
    print("ERROR: Database is set to PostgreSQL!")
    print("!" * 60)
    print()
    print("Your .env file has the wrong DATABASE_URL.")
    print("Please edit .env and change the DATABASE_URL line to:")
    print("  DATABASE_URL=sqlite:///./master_creator.db")
    print()
    print("Then run this script again.")
    print("!" * 60)
    input("Press Enter to exit...")
    sys.exit(1)
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
