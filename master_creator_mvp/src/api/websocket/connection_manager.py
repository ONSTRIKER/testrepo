"""
WebSocket Connection Manager

Manages WebSocket connections for real-time updates across the application.
Supports multiple connection types: dashboard, pipeline, student updates.
"""

import json
import logging
from typing import Dict, List, Set
from fastapi import WebSocket

logger = logging.getLogger("websocket.manager")


class ConnectionManager:
    """
    Manages WebSocket connections and broadcasts updates.

    Supports multiple connection types:
    - dashboard: Class-wide dashboard updates
    - student: Individual student updates
    - pipeline: Pipeline execution updates
    """

    def __init__(self):
        # Active connections by type and ID
        # Format: {connection_type: {resource_id: [WebSocket, WebSocket, ...]}}
        self.active_connections: Dict[str, Dict[str, List[WebSocket]]] = {
            "dashboard": {},
            "student": {},
            "pipeline": {},
        }

    async def connect(self, websocket: WebSocket, connection_type: str, resource_id: str):
        """
        Accept new WebSocket connection.

        Args:
            websocket: FastAPI WebSocket instance
            connection_type: Type of connection ("dashboard", "student", "pipeline")
            resource_id: ID of the resource (class_id, student_id, pipeline_id)
        """
        await websocket.accept()

        if connection_type not in self.active_connections:
            self.active_connections[connection_type] = {}

        if resource_id not in self.active_connections[connection_type]:
            self.active_connections[connection_type][resource_id] = []

        self.active_connections[connection_type][resource_id].append(websocket)

        logger.info(
            f"WebSocket connected: {connection_type}/{resource_id} "
            f"(Total: {len(self.active_connections[connection_type][resource_id])} connections)"
        )

        # Send connection confirmation
        await self.send_personal_message(
            websocket,
            {
                "type": "connection_established",
                "connection_type": connection_type,
                "resource_id": resource_id,
                "message": f"Connected to {connection_type} updates for {resource_id}"
            }
        )

    def disconnect(self, websocket: WebSocket, connection_type: str, resource_id: str):
        """
        Remove WebSocket connection.

        Args:
            websocket: FastAPI WebSocket instance
            connection_type: Type of connection
            resource_id: ID of the resource
        """
        if (connection_type in self.active_connections and
            resource_id in self.active_connections[connection_type]):

            try:
                self.active_connections[connection_type][resource_id].remove(websocket)
                logger.info(f"WebSocket disconnected: {connection_type}/{resource_id}")

                # Clean up empty lists
                if not self.active_connections[connection_type][resource_id]:
                    del self.active_connections[connection_type][resource_id]
            except ValueError:
                pass

    async def send_personal_message(self, websocket: WebSocket, message: dict):
        """
        Send message to a specific WebSocket connection.

        Args:
            websocket: WebSocket to send to
            message: Message dict to send
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def broadcast_to_type(self, connection_type: str, resource_id: str, message: dict):
        """
        Broadcast message to all connections of a specific type/resource.

        Args:
            connection_type: Type of connection
            resource_id: ID of the resource
            message: Message dict to broadcast
        """
        if (connection_type not in self.active_connections or
            resource_id not in self.active_connections[connection_type]):
            logger.debug(f"No active connections for {connection_type}/{resource_id}")
            return

        connections = self.active_connections[connection_type][resource_id].copy()

        logger.info(
            f"Broadcasting to {len(connections)} connections "
            f"({connection_type}/{resource_id}): {message.get('type', 'unknown')}"
        )

        # Track failed connections
        failed_connections = []

        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                failed_connections.append(connection)

        # Remove failed connections
        for connection in failed_connections:
            self.disconnect(connection, connection_type, resource_id)

    async def broadcast_student_update(self, class_id: str, student_id: str, update_data: dict):
        """
        Broadcast student update to both dashboard and individual student connections.

        Args:
            class_id: Class ID
            student_id: Student ID
            update_data: Update data
        """
        message = {
            "type": "student_update",
            "student_id": student_id,
            "class_id": class_id,
            "data": update_data,
            "timestamp": update_data.get("timestamp", "")
        }

        # Broadcast to class dashboard
        await self.broadcast_to_type("dashboard", class_id, message)

        # Broadcast to individual student connections
        await self.broadcast_to_type("student", student_id, message)

    async def broadcast_assessment_graded(self, class_id: str, student_id: str, assessment_data: dict):
        """
        Broadcast assessment grading completion.

        Args:
            class_id: Class ID
            student_id: Student ID
            assessment_data: Graded assessment data
        """
        message = {
            "type": "assessment_graded",
            "student_id": student_id,
            "class_id": class_id,
            "data": assessment_data
        }

        await self.broadcast_to_type("dashboard", class_id, message)
        await self.broadcast_to_type("student", student_id, message)

    async def broadcast_mastery_update(self, class_id: str, student_id: str, mastery_data: dict):
        """
        Broadcast mastery level update (from BKT updates).

        Args:
            class_id: Class ID
            student_id: Student ID
            mastery_data: Updated mastery data
        """
        message = {
            "type": "mastery_update",
            "student_id": student_id,
            "class_id": class_id,
            "data": mastery_data
        }

        await self.broadcast_to_type("dashboard", class_id, message)
        await self.broadcast_to_type("student", student_id, message)

    async def broadcast_recommendation_generated(self, class_id: str, student_id: str, recommendations: dict):
        """
        Broadcast adaptive recommendation generation (Engine 4).

        Args:
            class_id: Class ID
            student_id: Student ID
            recommendations: Generated recommendations
        """
        message = {
            "type": "recommendation_generated",
            "student_id": student_id,
            "class_id": class_id,
            "data": recommendations
        }

        await self.broadcast_to_type("dashboard", class_id, message)
        await self.broadcast_to_type("student", student_id, message)

    def get_connection_count(self, connection_type: str = None, resource_id: str = None) -> int:
        """
        Get count of active connections.

        Args:
            connection_type: Optional filter by type
            resource_id: Optional filter by resource ID

        Returns:
            Number of active connections
        """
        if connection_type is None:
            # Total across all types
            return sum(
                sum(len(conns) for conns in type_dict.values())
                for type_dict in self.active_connections.values()
            )

        if resource_id is None:
            # Total for connection type
            return sum(
                len(conns) for conns in self.active_connections.get(connection_type, {}).values()
            )

        # Specific resource
        return len(
            self.active_connections.get(connection_type, {}).get(resource_id, [])
        )


# Global connection manager instance
manager = ConnectionManager()
