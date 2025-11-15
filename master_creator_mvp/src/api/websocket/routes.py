"""
WebSocket Routes

Real-time update endpoints for dashboard, students, and pipeline monitoring.
"""

import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .connection_manager import manager

logger = logging.getLogger("websocket.routes")

router = APIRouter()


@router.websocket("/ws/dashboard/{class_id}")
async def websocket_dashboard(websocket: WebSocket, class_id: str):
    """
    WebSocket endpoint for class dashboard updates.

    Receives real-time updates for:
    - Student mastery changes
    - Assessment gradings
    - Recommendation generations
    - Student profile updates

    URL: ws://localhost:8080/ws/dashboard/{class_id}
    """
    await manager.connect(websocket, "dashboard", class_id)

    try:
        while True:
            # Keep connection alive and listen for client messages
            data = await websocket.receive_text()

            # Echo received messages (for heartbeat/ping)
            if data == "ping":
                await manager.send_personal_message(websocket, {"type": "pong"})

            logger.debug(f"Received from dashboard/{class_id}: {data}")

    except WebSocketDisconnect:
        manager.disconnect(websocket, "dashboard", class_id)
        logger.info(f"Dashboard disconnected: {class_id}")


@router.websocket("/ws/student/{student_id}")
async def websocket_student(websocket: WebSocket, student_id: str):
    """
    WebSocket endpoint for individual student updates.

    Receives real-time updates for:
    - Personal mastery changes
    - Assessment results
    - Generated recommendations
    - Profile changes

    URL: ws://localhost:8080/ws/student/{student_id}
    """
    await manager.connect(websocket, "student", student_id)

    try:
        while True:
            data = await websocket.receive_text()

            if data == "ping":
                await manager.send_personal_message(websocket, {"type": "pong"})

            logger.debug(f"Received from student/{student_id}: {data}")

    except WebSocketDisconnect:
        manager.disconnect(websocket, "student", student_id)
        logger.info(f"Student disconnected: {student_id}")


@router.websocket("/ws/pipeline/{job_id}")
async def websocket_pipeline(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for pipeline execution updates.

    Receives real-time updates for:
    - Pipeline stage completions
    - Engine execution status
    - Error notifications
    - Completion events

    URL: ws://localhost:8080/ws/pipeline/{job_id}
    """
    await manager.connect(websocket, "pipeline", job_id)

    try:
        while True:
            data = await websocket.receive_text()

            if data == "ping":
                await manager.send_personal_message(websocket, {"type": "pong"})

            logger.debug(f"Received from pipeline/{job_id}: {data}")

    except WebSocketDisconnect:
        manager.disconnect(websocket, "pipeline", job_id)
        logger.info(f"Pipeline disconnected: {job_id}")


@router.get("/ws/status")
async def websocket_status():
    """
    Get WebSocket connection statistics.

    GET /api/ws/status

    Returns:
        Connection counts by type
    """
    return {
        "status": "ok",
        "connections": {
            "dashboard": manager.get_connection_count("dashboard"),
            "student": manager.get_connection_count("student"),
            "pipeline": manager.get_connection_count("pipeline"),
            "total": manager.get_connection_count()
        }
    }
