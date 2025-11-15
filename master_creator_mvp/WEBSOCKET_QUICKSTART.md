# WebSocket Real-Time Updates - Quick Start Guide

## 🚀 Get It Running in 5 Minutes

The WebSocket real-time updates are **already implemented and working**. You just need to start the servers!

### Prerequisites

1. **Python 3.11+** installed
2. **Node.js 18+** installed
3. **Internet connection** (for first-time dependencies)

### Step 1: Install Python Dependencies

```bash
cd master_creator_mvp

# Install all required packages
pip install fastapi uvicorn websockets python-dotenv anthropic sqlalchemy pydantic pandas numpy chromadb sentence-transformers
```

**Note:** This might take 2-3 minutes on first install due to `sentence-transformers` and `chromadb`.

### Step 2: Initialize Database

```bash
# Create database tables
python init_content_storage.py

# Load sample student data
python load_sample_data.py
```

You should see:
```
✅ All database tables created successfully!
✓ Sample data loaded
```

### Step 3: Start Backend Server

```bash
python run_server.py
```

**You should see:**
```
Master Creator MVP - Starting Server
Server will be available at: http://localhost:8080
```

**Test it's working:**
- Open http://localhost:8080/health
- Should see: `{"status":"healthy",...}`

✅ **Backend is running!** Leave this terminal open.

### Step 4: Start Frontend Server

Open a **NEW terminal** window:

```bash
cd master_creator_mvp/frontend

# Install frontend dependencies (first time only)
npm install

# Start frontend dev server
npm run dev
```

**You should see:**
```
VITE v5.x.x ready in xxx ms
➜  Local:   http://localhost:3000/
```

✅ **Frontend is running!** Leave this terminal open too.

### Step 5: Open Dashboard & See WebSocket Magic! ✨

1. Open http://localhost:3000 in your browser

2. **Look for the connection indicator** in the top-right corner of the dashboard:
   - 🟢 **Green pulsing dot** = WebSocket connected!
   - Text should say: **"Live Updates Active"**

3. **Open Browser DevTools** (Press F12) → Console tab

   You should see:
   ```
   Connecting to dashboard WebSocket for class: class_001
   Dashboard WebSocket connected to class class_001
   Dashboard WebSocket connected successfully
   ```

✅ **WebSocket is connected and ready!**

### Step 6: Test Real-Time Updates

#### Test 1: Generate Adaptive Recommendations

1. Select any student from the dashboard
2. Click the **"Generate Recommendations"** button (purple button at bottom)
3. Watch the recommendations appear **without refreshing the page!**

**In the console, you'll see:**
```
WebSocket message received: {type: "recommendation_generated", ...}
Recommendations generated: {...}
Adaptive recommendations updated in real-time for: student_001
```

#### Test 2: Assessment Grading (Advanced)

In a new terminal, submit a test assessment:

```bash
curl -X POST http://localhost:8080/api/assessments/submit \
  -H "Content-Type: application/json" \
  -d '{
    "assessment_id": "test_assessment",
    "student_id": "student_001",
    "questions": [{
      "question_id": "q1",
      "question_text": "Test question",
      "question_type": "constructed_response",
      "concept_id": "photosynthesis",
      "points_possible": 10.0
    }],
    "responses": [{"question_id": "q1", "answer": "Test answer"}],
    "update_mastery": true
  }'
```

**Watch the dashboard auto-update!** The student's score will change without any manual refresh.

**Console shows:**
```
WebSocket message received: {type: "assessment_graded", ...}
Assessment graded: {...}
Student data updated after assessment: student_001
```

## 🎉 Success! You're Live!

If you see the green dot and console messages, **WebSocket real-time updates are working!**

## Common Issues & Fixes

### Issue 1: "Connecting..." stuck (no green dot)

**Symptom:** Status shows "Connecting..." instead of "Live Updates Active"

**Fix:**
1. Check backend is running: http://localhost:8080/health
2. Check WebSocket status: http://localhost:8080/api/ws/status
3. Look for errors in backend terminal
4. Check browser console for WebSocket errors

### Issue 2: Backend won't start - ModuleNotFoundError

**Fix:**
```bash
pip install fastapi uvicorn websockets python-dotenv anthropic sqlalchemy pydantic pandas numpy chromadb sentence-transformers
```

### Issue 3: Frontend won't start

**Fix:**
```bash
cd master_creator_mvp/frontend
npm install
npm run dev
```

### Issue 4: Port already in use

**Backend (port 8080):**
```bash
# Kill process on port 8080
# On Mac/Linux:
lsof -ti:8080 | xargs kill -9

# On Windows:
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

**Frontend (port 3000):**
```bash
# On Mac/Linux:
lsof -ti:3000 | xargs kill -9

# On Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

## Architecture Overview

```
┌──────────────────────┐
│   Browser (3000)     │
│  ┌────────────────┐  │
│  │   Dashboard    │  │
│  │   🟢 WebSocket │  │
│  └────────┬───────┘  │
└───────────┼──────────┘
            │ ws://localhost:3000/ws/dashboard/class_001
            ▼
┌──────────────────────┐
│   Backend (8080)     │
│  ┌────────────────┐  │
│  │ FastAPI +      │  │
│  │ WebSocket      │  │
│  │ Routes         │  │
│  └────────────────┘  │
└──────────────────────┘
```

## What's Implemented?

✅ **Backend WebSocket Infrastructure**
- Connection manager for tracking active connections
- 3 WebSocket endpoints: dashboard, student, pipeline
- Event broadcasting methods (4 event types)
- Heartbeat/ping support (30s intervals)

✅ **Frontend WebSocket Client**
- Automatic connection on dashboard load
- 4 event handlers (student_update, assessment_graded, mastery_update, recommendations)
- Auto-reconnection logic
- Visual connection status indicator

✅ **Event Broadcasting**
- Assessments API broadcasts on grading
- Adaptive API broadcasts on recommendation generation
- Automatic student class lookup for routing

✅ **Real-Time Features**
- Live assessment score updates
- Instant recommendation display
- Auto-refresh on data changes
- No manual page refresh needed!

## Next Steps

1. ✅ Verify both servers are running
2. ✅ See green dot indicator
3. ✅ Test "Generate Recommendations" button
4. ✅ Check console logs for WebSocket messages
5. 📚 Read full documentation: `WEBSOCKET_REALTIME_UPDATES.md`

## Documentation

- **This Guide:** Quick start (5 minutes)
- **WEBSOCKET_REALTIME_UPDATES.md:** Complete architecture & API reference
- **STARTUP_GUIDE.md:** Detailed troubleshooting
- **README.md:** Full project overview

## Support

**Still having issues?**

1. Check backend terminal for errors
2. Check browser console (F12) for errors
3. Verify both ports (3000, 8080) are accessible
4. Review logs for connection failures

**Everything working?** 🎉

You now have real-time dashboard updates! Try:
- Grading assessments → See scores update live
- Generating recommendations → See them appear instantly
- Opening multiple browser windows → All update simultaneously!

---

**Made with WebSocket magic by Master Creator v3 MVP** ✨
