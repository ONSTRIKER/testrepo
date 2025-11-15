"""
Master Creator v3 MVP - FastAPI Application

Main FastAPI application with all route handlers for the Teacher UI.

Routes:
- /api/lessons - Lesson generation (Engine 0, 1)
- /api/students - Student management (Student Model)
- /api/assessments - Assessment grading
- /api/worksheets - Worksheet generation (Engine 2, 3)
- /api/pipeline - Full pipeline orchestration
- /api/adaptive - Adaptive personalization (Engine 4)
- /api/feedback - Feedback loop (Engine 6)
- /health - Health check
"""

# Load environment variables from .env file first
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from .routes import lessons, students, assessments, worksheets, pipeline, adaptive
from .websocket import routes as websocket_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("master_creator_api")

# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# FASTAPI APP INITIALIZATION
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP

app = FastAPI(
    title="Master Creator v3 MVP API",
    description="AI-powered adaptive learning system for K-12 special education",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# CORS MIDDLEWARE
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:8501",  # Streamlit
        "http://localhost:8000",  # FastAPI dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# ROUTERS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP

app.include_router(lessons.router, prefix="/api/lessons", tags=["Lessons"])
app.include_router(students.router, prefix="/api/students", tags=["Students"])
app.include_router(assessments.router, prefix="/api/assessments", tags=["Assessments"])
app.include_router(worksheets.router, prefix="/api/worksheets", tags=["Worksheets"])
app.include_router(pipeline.router, prefix="/api/pipeline", tags=["Pipeline"])
app.include_router(adaptive.router, prefix="/api/adaptive", tags=["Adaptive"])
app.include_router(websocket_routes.router, tags=["WebSocket"])

# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# HEALTH CHECK
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Master Creator v3 MVP API",
        "version": "1.0.0",
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Master Creator v3 MVP API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/health",
        "endpoints": {
            "lessons": "/api/lessons",
            "students": "/api/students",
            "assessments": "/api/assessments",
            "worksheets": "/api/worksheets",
            "pipeline": "/api/pipeline",
            "adaptive": "/api/adaptive",
        },
        "websockets": {
            "dashboard": "ws://localhost:8080/ws/dashboard/{class_id}",
            "student": "ws://localhost:8080/ws/student/{student_id}",
            "pipeline": "ws://localhost:8080/ws/pipeline/{job_id}",
            "status": "/api/ws/status",
        },
    }


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# EXCEPTION HANDLERS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions."""
    logger.error(f"ValueError: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid input", "detail": str(exc)},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# STARTUP/SHUTDOWN EVENTS
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP

@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup."""
    logger.info("Master Creator v3 MVP API starting up...")
    logger.info("API documentation available at /api/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown."""
    logger.info("Master Creator v3 MVP API shutting down...")


# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
# RUN SERVER (for development)
# PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
