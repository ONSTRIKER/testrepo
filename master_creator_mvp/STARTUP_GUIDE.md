# Master Creator v3 MVP - Startup Guide

## Quick Start

### 1. Initialize Database (First Time Only)

```bash
cd master_creator_mvp
python init_content_storage.py
python load_sample_data.py
```

### 2. Start Backend Server

Open a terminal and run:

```bash
cd master_creator_mvp
python run_server.py
```

You should see:
```
Master Creator MVP - Starting Server
Server will be available at: http://localhost:8080
API Documentation: http://localhost:8080/api/docs
```

**Verify backend is running:**
- Open http://localhost:8080/health in your browser
- You should see: `{"status":"healthy","service":"Master Creator v3 MVP API","version":"1.0.0"}`

### 3. Start Frontend Server

Open a **NEW** terminal (keep backend running) and run:

```bash
cd master_creator_mvp/frontend
npm install  # Only needed first time
npm run dev
```

You should see:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:3000/
```

### 4. Open Dashboard

Open http://localhost:3000 in your browser.

**Check WebSocket connection:**
1. Look for the connection indicator in the top-right of the dashboard header
2. You should see a **green pulsing dot** with "Live Updates Active"
3. Open Browser DevTools (F12) → Console tab
4. You should see: `Dashboard WebSocket connected to class: class_001`

## Troubleshooting

### Backend Won't Start

**Error: ModuleNotFoundError**
```bash
cd master_creator_mvp
pip install -r requirements.txt
```

**Error: Database not found**
```bash
python init_content_storage.py
python load_sample_data.py
```

### Frontend Won't Start

**Error: npm not found**
- Install Node.js from https://nodejs.org/

**Error: Dependencies not installed**
```bash
cd master_creator_mvp/frontend
npm install
```

**Error: Port 3000 already in use**
```bash
# Kill the process using port 3000
# On Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# On Mac/Linux:
lsof -ti:3000 | xargs kill -9
```

### WebSocket Not Connecting

**Status shows "Connecting..." instead of "Live Updates Active"**

1. **Check backend is running on port 8080:**
   ```bash
   curl http://localhost:8080/health
   ```

2. **Check WebSocket endpoint:**
   ```bash
   curl http://localhost:8080/api/ws/status
   ```
   Should return:
   ```json
   {
     "status": "online",
     "active_connections": {...}
   }
   ```

3. **Check browser console for errors:**
   - Open DevTools (F12) → Console tab
   - Look for WebSocket errors
   - Common issues:
     - "WebSocket connection failed" - Backend not running
     - "Connection refused" - Wrong port or proxy issue
     - "404 Not Found" - WebSocket routes not registered

4. **Verify proxy configuration:**
   - Check `frontend/vite.config.js` has WebSocket proxy configured
   - Should see:
     ```javascript
     '/ws': {
       target: 'ws://localhost:8080',
       ws: true,
     }
     ```

### Testing WebSocket Events

Once connected, test real-time updates:

1. **Test Adaptive Recommendations:**
   - Click "Generate Recommendations" button in dashboard
   - Recommendations should appear without page refresh
   - Console should show: "Recommendations generated:"

2. **Test Assessment Grading (via API):**
   ```bash
   # Submit a test assessment
   curl -X POST http://localhost:8080/api/assessments/submit \
     -H "Content-Type: application/json" \
     -d '{
       "assessment_id": "test_assessment",
       "student_id": "student_001",
       "questions": [...],
       "responses": [...],
       "update_mastery": true
     }'
   ```
   - Dashboard should auto-update student scores
   - Console should show: "Assessment graded:"

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Port 3000)                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │   StudentPerformanceDashboard.jsx                    │   │
│  │   - WebSocket connection to /ws/dashboard/{class}    │   │
│  │   - Real-time event handlers                         │   │
│  │   - Auto-refresh on data changes                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                  │
│                           │ WebSocket + REST API             │
│                           ▼                                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Backend (Port 8080)                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │   FastAPI Application (main.py)                      │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │   WebSocket Routes (/ws/*)                           │   │
│  │   - Dashboard connections                            │   │
│  │   - Student connections                              │   │
│  │   - Pipeline connections                             │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │   REST API Routes (/api/*)                           │   │
│  │   - Assessments (broadcasts on grade)               │   │
│  │   - Adaptive (broadcasts on recommendations)        │   │
│  │   - Students, Lessons, Worksheets, etc.             │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │   Connection Manager                                 │   │
│  │   - Tracks active WebSocket connections              │   │
│  │   - Broadcasts events to connected clients           │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                  │
│                           ▼                                  │
│                    SQLite Database                           │
│                  (master_creator.db)                         │
└─────────────────────────────────────────────────────────────┘
```

## Development Workflow

### Normal Development

1. Start backend (terminal 1):
   ```bash
   cd master_creator_mvp
   python run_server.py
   ```

2. Start frontend (terminal 2):
   ```bash
   cd master_creator_mvp/frontend
   npm run dev
   ```

3. Make changes to code
4. Frontend auto-reloads (Vite hot reload)
5. Backend: Restart server manually for changes

### Testing Changes

1. Open http://localhost:3000
2. Open Browser DevTools (F12) → Console
3. Watch for WebSocket messages and logs
4. Test features (generate recommendations, etc.)

## Port Reference

- **3000** - Frontend (Vite dev server)
- **8080** - Backend (FastAPI server)

## Environment Variables

Required in `master_creator_mvp/.env`:

```bash
# API Keys
ANTHROPIC_API_KEY=sk-ant-...

# Database
DATABASE_URL=sqlite:///./master_creator.db

# Optional
LOG_LEVEL=INFO
```

## Next Steps

1. ✅ Start both servers
2. ✅ Verify WebSocket connection (green dot)
3. ✅ Test dashboard loads student data
4. ✅ Test "Generate Recommendations" button
5. ✅ Check real-time updates work

## Support

- Documentation: See README.md
- API Docs: http://localhost:8080/api/docs
- WebSocket Guide: See WEBSOCKET_REALTIME_UPDATES.md
- Architecture: See CONTENT_STORAGE_IMPLEMENTATION.md
