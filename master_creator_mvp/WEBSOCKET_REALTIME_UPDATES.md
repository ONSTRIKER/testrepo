# WebSocket Real-Time Updates Implementation

## Overview

This document describes the implementation of WebSocket-based real-time updates for the Master Creator v3 MVP Student Performance Dashboard, enabling live updates when student data changes without requiring manual page refreshes.

## Problem Solved

Previously, the Student Performance Dashboard required manual refreshing to see updated student data after:
- Assessments were graded
- Adaptive recommendations were generated
- Student mastery levels changed

This implementation provides instant, automatic updates to the dashboard when any of these events occur.

## Architecture

### Backend Components

#### 1. WebSocket Connection Manager (`src/api/websocket/connection_manager.py`)

Manages all WebSocket connections and broadcasting logic.

**Key Features:**
- Tracks active connections by type (dashboard, student, pipeline)
- Provides broadcasting methods for different event types
- Handles connection lifecycle (connect, disconnect, cleanup)
- Supports heartbeat/ping for connection health
- Thread-safe connection management

**Connection Types:**
- `dashboard`: Class-level connections (e.g., `ws://localhost:8080/ws/dashboard/{class_id}`)
- `student`: Individual student connections (e.g., `ws://localhost:8080/ws/student/{student_id}`)
- `pipeline`: Pipeline execution connections (e.g., `ws://localhost:8080/ws/pipeline/{job_id}`)

**Broadcasting Methods:**
```python
# Broadcast student data update
await manager.broadcast_student_update(class_id, student_id, update_data)

# Broadcast assessment grading completion
await manager.broadcast_assessment_graded(class_id, student_id, assessment_data)

# Broadcast mastery level update
await manager.broadcast_mastery_update(class_id, student_id, mastery_data)

# Broadcast adaptive recommendation generation
await manager.broadcast_recommendation_generated(class_id, student_id, recommendations)
```

#### 2. WebSocket Routes (`src/api/websocket/routes.py`)

Defines WebSocket endpoint handlers.

**Endpoints:**
- `GET /ws/dashboard/{class_id}` - Connect to class dashboard updates
- `GET /ws/student/{student_id}` - Connect to individual student updates
- `GET /ws/pipeline/{job_id}` - Connect to pipeline execution updates
- `GET /api/ws/status` - Get WebSocket connection statistics

**Message Flow:**
1. Client connects via WebSocket
2. Server sends `connection_confirmed` message
3. Client can send `ping` to check connection health (receives `pong`)
4. Server broadcasts updates as they occur
5. Client disconnects when done

#### 3. Event Broadcasting Integration

WebSocket events are broadcasted from API endpoints when data changes:

**Assessment Grading (`src/api/routes/assessments.py`):**
```python
# After grading assessment
await manager.broadcast_assessment_graded(
    class_id=class_id,
    student_id=student_id,
    assessment_data={
        "assessment_id": assessment_id,
        "grading_id": graded.grading_id,
        "score_percentage": graded.score_percentage,
        "total_points": graded.total_points_earned,
        "graded_at": graded.graded_at
    }
)
```

**Adaptive Recommendations (`src/api/routes/adaptive.py`):**
```python
# After generating recommendations
await manager.broadcast_recommendation_generated(
    class_id=class_id,
    student_id=student_id,
    recommendations=path.model_dump()
)
```

### Frontend Components

#### 1. WebSocket API Methods (`frontend/src/services/api.js`)

Provides easy-to-use WebSocket connection methods.

**Methods:**
```javascript
// Connect to dashboard updates
api.connectToDashboard(classId, onMessage, onError)

// Connect to student updates
api.connectToStudent(studentId, onMessage, onError)

// Disconnect
api.disconnectDashboard()
api.disconnectStudent()
api.disconnectAll()
```

**Features:**
- Automatic heartbeat (30-second ping intervals)
- Reconnection handling
- Error callbacks
- Message parsing and routing

#### 2. Dashboard Integration (`frontend/src/components/StudentPerformanceDashboard.jsx`)

Real-time updates integrated into the dashboard component.

**State Management:**
```javascript
const [wsConnected, setWsConnected] = useState(false);
```

**WebSocket Connection (useEffect):**
- Establishes connection when component mounts
- Reconnects when `classId` changes
- Cleans up connection on unmount

**Message Handlers:**
- `handleStudentUpdate(data)` - Updates student data in real-time
- `handleAssessmentGraded(data)` - Reloads student data after assessment
- `handleMasteryUpdate(data)` - Updates mastery levels
- `handleRecommendationGenerated(data)` - Shows new recommendations

**Visual Indicator:**
- Green pulsing dot: WebSocket connected
- Gray dot: Connecting or disconnected
- Status text: "Live Updates Active" or "Connecting..."

## Event Types

### 1. Connection Confirmed
```json
{
  "type": "connection_confirmed",
  "connection_type": "dashboard",
  "resource_id": "class_001",
  "timestamp": "2025-11-15T10:30:00Z"
}
```

### 2. Student Update
```json
{
  "type": "student_update",
  "student_id": "student_123",
  "class_id": "class_001",
  "update_data": {
    "field": "value"
  },
  "timestamp": "2025-11-15T10:30:00Z"
}
```

### 3. Assessment Graded
```json
{
  "type": "assessment_graded",
  "student_id": "student_123",
  "class_id": "class_001",
  "assessment_data": {
    "assessment_id": "assessment_456",
    "grading_id": "grading_789",
    "score_percentage": 85.5,
    "total_points": 42.75,
    "graded_at": "2025-11-15T10:30:00Z"
  },
  "timestamp": "2025-11-15T10:30:00Z"
}
```

### 4. Mastery Update
```json
{
  "type": "mastery_update",
  "student_id": "student_123",
  "class_id": "class_001",
  "mastery_data": {
    "concept_id": "photosynthesis",
    "new_mastery": 0.85,
    "previous_mastery": 0.72
  },
  "timestamp": "2025-11-15T10:30:00Z"
}
```

### 5. Recommendation Generated
```json
{
  "type": "recommendation_generated",
  "student_id": "student_123",
  "class_id": "class_001",
  "recommendations": {
    "path_id": "path_789",
    "recommendations": [
      "Focus on cellular respiration next",
      "Review photosynthesis light reactions"
    ],
    "zpd_recommendations": [
      "Practice problems at 70-80% difficulty"
    ]
  },
  "timestamp": "2025-11-15T10:30:00Z"
}
```

### 6. Heartbeat (Ping/Pong)
```json
{
  "type": "pong"
}
```

## User Flow

### Dashboard User Experience

1. **User opens Student Performance Dashboard**
   - Component mounts and establishes WebSocket connection
   - Connection indicator shows "Connecting..."
   - Initial data loaded via REST API

2. **WebSocket connects successfully**
   - Connection indicator shows green pulsing dot
   - Status changes to "Live Updates Active"
   - Dashboard is now ready for real-time updates

3. **Teacher grades an assessment (different tab/session)**
   - Assessment grading endpoint broadcasts event
   - WebSocket receives `assessment_graded` message
   - Dashboard automatically reloads student's data
   - Student's score and mastery level update in real-time
   - No manual refresh needed!

4. **Teacher generates recommendations**
   - User clicks "Generate Recommendations" button
   - Engine 4 generates personalized learning path
   - WebSocket broadcasts `recommendation_generated` event
   - Recommendations appear instantly in dashboard
   - If viewing same student, recommendations update automatically

5. **User switches students or closes dashboard**
   - WebSocket connection cleanly disconnected
   - Resources cleaned up
   - Connection indicator resets

## Files Created

1. **`src/api/websocket/__init__.py`** - Package initialization
2. **`src/api/websocket/connection_manager.py`** - Connection management (~200 lines)
3. **`src/api/websocket/routes.py`** - WebSocket endpoints (~150 lines)

## Files Modified

1. **`src/api/main.py`**
   - Added WebSocket router import
   - Registered WebSocket routes
   - Added WebSocket URLs to root endpoint

2. **`frontend/src/services/api.js`**
   - Added separate WebSocket instances (dashboardWs, studentWs, pipelineWs)
   - Added `connectToDashboard()` method
   - Added `connectToStudent()` method
   - Added `disconnectDashboard()`, `disconnectStudent()`, `disconnectAll()` methods
   - Added heartbeat functionality (30s ping intervals)

3. **`frontend/src/components/StudentPerformanceDashboard.jsx`**
   - Added `wsConnected` state
   - Added WebSocket connection useEffect
   - Added 4 message handlers (student update, assessment graded, mastery update, recommendations)
   - Added connection status indicator to header
   - Automatic data refresh on events

4. **`src/api/routes/assessments.py`**
   - Added WebSocket manager import
   - Added broadcasting in `submit_assessment()` endpoint
   - Added broadcasting in `batch_grade_assessments()` endpoint

5. **`src/api/routes/adaptive.py`**
   - Added WebSocket manager import
   - Added StudentModelInterface import
   - Added broadcasting in `generate_student_path()` endpoint
   - Added broadcasting in `generate_adaptive_plan()` endpoint

## Benefits

1. **Real-Time Updates**: Dashboard updates instantly when data changes
2. **Better UX**: No manual refresh needed - updates appear automatically
3. **Live Collaboration**: Multiple teachers can see updates simultaneously
4. **Immediate Feedback**: See assessment results appear as they're graded
5. **Scalable**: Connection manager handles multiple concurrent connections
6. **Reliable**: Heartbeat mechanism detects and handles connection issues
7. **Clean Architecture**: Separation of concerns (manager, routes, broadcasting)

## Testing

### Manual Testing Steps

1. **Start Backend:**
```bash
python run_server.py
```

2. **Start Frontend:**
```bash
cd frontend
npm run dev
```

3. **Open Dashboard:**
   - Navigate to http://localhost:3000
   - Verify connection indicator shows "Live Updates Active"
   - Open browser DevTools Console to see WebSocket logs

4. **Test Assessment Grading:**
   - In another tab/window, submit an assessment via API
   - Watch dashboard automatically update student scores
   - Verify console shows "Assessment graded" message

5. **Test Recommendations:**
   - Click "Generate Recommendations" button
   - Verify recommendations appear without refresh
   - Check console for "Recommendations generated" message

6. **Test Connection Stability:**
   - Leave dashboard open for 5+ minutes
   - Verify heartbeat keeps connection alive
   - Switch between students and verify reconnection

### WebSocket Status Endpoint

```bash
# Check connection statistics
curl http://localhost:8080/api/ws/status
```

Returns:
```json
{
  "status": "online",
  "active_connections": {
    "dashboard": 2,
    "student": 1,
    "pipeline": 0
  },
  "total_connections": 3
}
```

## Production Considerations

### Current Implementation (Development)
- In-memory connection storage
- Single-server deployment
- WebSocket connections on same process as API

### Production Recommendations
1. **Use Redis for Connection State**
   - Store connection mapping in Redis
   - Enable horizontal scaling across multiple servers
   - Persist connection state across server restarts

2. **Load Balancing**
   - Use sticky sessions for WebSocket connections
   - Or implement Redis-backed pub/sub for broadcasting
   - Consider dedicated WebSocket server(s)

3. **Connection Limits**
   - Implement connection limits per class/student
   - Add rate limiting for broadcasts
   - Monitor connection count and memory usage

4. **Security**
   - Add authentication to WebSocket connections
   - Verify user has access to class/student data
   - Implement connection timeout policies
   - Add CORS configuration for WebSocket endpoints

5. **Monitoring**
   - Log connection/disconnection events
   - Track broadcast failures
   - Monitor WebSocket server health
   - Alert on connection anomalies

## Future Enhancements

1. **Selective Updates**
   - Only send changed fields instead of full reload
   - Reduce API calls by including data in WebSocket message
   - Implement optimistic updates

2. **Reconnection Strategy**
   - Automatic reconnection with exponential backoff
   - Resume from last known state
   - Queue updates during disconnection

3. **Additional Events**
   - Lesson generation complete
   - Worksheet creation complete
   - IEP modification applied
   - Diagnostic complete

4. **Presence Indicators**
   - Show which teachers are viewing dashboard
   - Indicate active editing/grading sessions
   - Collaborative features

5. **Message Compression**
   - Compress large payloads
   - Use binary WebSocket frames
   - Implement delta updates

## Troubleshooting

### Connection Not Established
- Check backend is running on port 8080
- Verify WebSocket URL in browser DevTools (Network tab, filter WS)
- Check CORS configuration in `main.py`
- Look for errors in browser console

### Updates Not Appearing
- Verify broadcasting code is being called (check backend logs)
- Confirm class_id matches between dashboard and event
- Check message handler is processing correct event type
- Verify student data reload is working

### Connection Drops
- Check heartbeat is functioning (30s ping intervals)
- Verify network stability
- Look for server restarts or crashes
- Check browser console for WebSocket errors

## References

- FastAPI WebSocket documentation: https://fastapi.tiangolo.com/advanced/websockets/
- WebSocket MDN reference: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket
- Connection management patterns: https://www.patterns.dev/

## Summary

This implementation provides a complete real-time update system for the Student Performance Dashboard using WebSocket connections. The architecture is clean, maintainable, and ready for production with minimal changes. Teachers can now see live updates as assessments are graded and recommendations are generated, significantly improving the user experience.
