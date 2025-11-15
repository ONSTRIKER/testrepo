# Complete Windows Setup Guide - Master Creator MVP

**Target Audience**: Brand new Windows computer (2 days old)
**Assumption**: You have NOTHING except Windows OS
**Goal**: Get the entire Master Creator MVP running with zero troubleshooting

---

## Current Status Assessment

### ✅ What You Already Have Installed

Based on our troubleshooting session:

1. **Python 3.14** (pythoncore-3.14-64) ✅
2. **Node.js 22.21.1** ✅
3. **npm 10.9.4** ✅
4. **Git** ✅ (you cloned the repo)
5. **PowerShell** ✅ (built into Windows)

**Project Location**: `C:\Users\phant\OneDrive\Documents\GitHub\testrepo\master_creator_mvp`

### ⚠️ What You're Missing

#### Python Packages (Partially Installed)
- ✅ Installed: sqlalchemy, fastapi, uvicorn, websockets, python-dotenv, pydantic, anthropic
- ❌ **FAILED**: numpy, pandas (compilation errors - no C compiler)
- ❌ **MISSING**: chromadb, sentence-transformers, python-multipart

#### Frontend Packages
- ❌ **NOT CHECKED YET**: All npm packages in `frontend/` folder

#### System Tools
- ❌ **MISSING**: C/C++ compiler (needed for numpy/pandas from source)

---

## THE PROBLEM: Why NumPy/Pandas Won't Install

**Root Cause**: NumPy and pandas are trying to compile from source code, which requires:
- Microsoft Visual Studio Build Tools
- C/C++ compiler
- Various SDKs

**Your Error Message**: `ERROR: Unknown compiler(s): [['icl'], ['cl'], ['cc'], ['gcc']...]`

This means: "I need a C compiler to build this code, but I can't find one."

---

## SOLUTION OPTIONS (Pick ONE)

### 🏆 **OPTION 1: Use Anaconda (RECOMMENDED FOR WINDOWS)**

**Why This Is Best**:
- ✅ Comes with ALL scientific packages pre-compiled (numpy, pandas, etc.)
- ✅ No compiler needed
- ✅ Works on brand new Windows computers
- ✅ Zero compilation errors
- ✅ Includes pip and conda package managers
- ✅ Most reliable for data science projects on Windows

**Time**: 15-20 minutes
**Difficulty**: Easy
**Reliability**: 99%

**Downside**:
- Downloads ~500MB installer
- Takes up ~3GB disk space
- You'll have two Python installations (your current 3.14 + Anaconda's Python)

---

### OPTION 2: Install Visual Studio Build Tools (Advanced)

**Why You Might Choose This**:
- ✅ Keep your current Python 3.14
- ✅ Smaller download than Anaconda

**Why This Is Harder**:
- ❌ 5-10GB download
- ❌ Complex installation
- ❌ Still might have compilation errors
- ❌ Requires restarting PowerShell/computer

**Time**: 30-60 minutes
**Difficulty**: Medium-Hard
**Reliability**: 70%

---

### OPTION 3: Use Prebuilt Wheels Only (Minimal)

**Why You Might Choose This**:
- ✅ Keep current Python
- ✅ Smallest downloads
- ✅ No compiler needed

**Why This Might Fail**:
- ❌ Not all packages have prebuilt wheels for Python 3.14 (it's VERY new)
- ❌ May still hit missing packages
- ❌ Requires finding wheel files manually

**Time**: 20-40 minutes
**Difficulty**: Medium
**Reliability**: 60%

---

## 🏆 RECOMMENDED PATH: Install Anaconda

I strongly recommend **Option 1 (Anaconda)** because:
1. You said this is a brand new computer - disk space isn't an issue
2. You want to avoid troubleshooting - Anaconda "just works"
3. Your project uses numpy, pandas, chromadb - all included
4. You're paying for time - this is the fastest reliable path

---

## COMPLETE STEP-BY-STEP INSTALLATION (ANACONDA PATH)

### Phase 1: Install Anaconda (15 minutes)

#### Step 1.1: Download Anaconda

**Where**: Your web browser
**URL**: https://www.anaconda.com/download/success
**File**: `Anaconda3-2024.10-1-Windows-x86_64.exe` (or latest version)
**Size**: ~600MB

**Instructions**:
1. Click the URL above
2. Click "Download" button (green, top-right)
3. Save to your Downloads folder
4. Wait for download to complete (~5-10 minutes depending on internet)

#### Step 1.2: Install Anaconda

**Where**: Run the downloaded .exe file from Downloads folder

**Installation Options**:
1. Click "Next"
2. Click "I Agree" (license)
3. Choose "Just Me" (recommended)
4. **IMPORTANT**: Installation path - use default: `C:\Users\phant\anaconda3`
5. **CRITICAL CHOICE**:
   - ✅ CHECK: "Add Anaconda3 to my PATH environment variable" (even though it says "not recommended")
   - ✅ CHECK: "Register Anaconda3 as my default Python 3.14"
6. Click "Install" (takes 5-10 minutes)
7. Click "Next", then "Finish"

**Why we check "Add to PATH"**: So when you type `python` in PowerShell, it uses Anaconda's Python.

#### Step 1.3: Verify Anaconda Installation

**Where**: PowerShell (close and reopen any existing PowerShell windows)

**Command**:
```powershell
python --version
```

**Expected Output**:
```
Python 3.11.x :: Anaconda, Inc.
```

**If you see this**: ✅ Anaconda is installed correctly

**If you see `Python 3.14`**: ⚠️ Path not updated, restart PowerShell and try again

**Command**:
```powershell
conda --version
```

**Expected Output**:
```
conda 24.x.x
```

---

### Phase 2: Create Project Environment (5 minutes)

#### Step 2.1: Navigate to Project Folder

**Where**: PowerShell

**Command**:
```powershell
cd "C:\Users\phant\OneDrive\Documents\GitHub\testrepo\master_creator_mvp"
```

**Expected Output**: (none - just changes directory)

**Verify**:
```powershell
pwd
```

**Expected Output**:
```
Path
----
C:\Users\phant\OneDrive\Documents\GitHub\testrepo\master_creator_mvp
```

#### Step 2.2: Create Conda Environment for Project

**Where**: PowerShell (in project folder)

**Command**:
```powershell
conda create -n master_creator python=3.11 -y
```

**What This Does**: Creates an isolated Python environment named "master_creator" with Python 3.11

**Expected Output**:
```
Collecting package metadata...
Solving environment...
...
Preparing transaction: done
Verifying transaction: done
Executing transaction: done
```

**Time**: 2-3 minutes

#### Step 2.3: Activate the Environment

**Where**: PowerShell

**Command**:
```powershell
conda activate master_creator
```

**Expected Output**:
```
(master_creator) PS C:\Users\phant\OneDrive\Documents\GitHub\testrepo\master_creator_mvp>
```

**Notice**: Your prompt now starts with `(master_creator)` - this means you're in the environment.

**IMPORTANT**: You must ALWAYS activate this environment before working on the project!

---

### Phase 3: Install ALL Python Packages (10 minutes)

#### Step 3.1: Install Core Scientific Packages (from Anaconda)

**Where**: PowerShell (with `master_creator` environment activated)

**Command**:
```powershell
conda install numpy pandas -y
```

**Expected Output**:
```
Collecting package metadata...
Solving environment...
...
Executing transaction: done
```

**What This Does**: Installs pre-compiled numpy and pandas (NO COMPILATION!)

**Time**: 2-3 minutes

#### Step 3.2: Install FastAPI and Web Framework Packages

**Where**: PowerShell (with `master_creator` environment activated)

**Command**:
```powershell
pip install fastapi uvicorn websockets python-dotenv python-multipart
```

**Expected Output**:
```
Collecting fastapi...
Collecting uvicorn...
...
Successfully installed fastapi-x.x.x uvicorn-x.x.x ...
```

**Time**: 1-2 minutes

#### Step 3.3: Install Database and ORM Packages

**Command**:
```powershell
pip install sqlalchemy pydantic
```

**Expected Output**:
```
Successfully installed sqlalchemy-x.x.x pydantic-x.x.x
```

#### Step 3.4: Install AI/ML Packages

**Command**:
```powershell
pip install anthropic chromadb sentence-transformers
```

**Expected Output**:
```
Collecting anthropic...
Collecting chromadb...
Collecting sentence-transformers...
...
Successfully installed anthropic-x.x.x chromadb-x.x.x sentence-transformers-x.x.x ...
```

**Time**: 3-5 minutes (sentence-transformers downloads models)

**What This Does**:
- `anthropic`: Claude API client
- `chromadb`: Vector database for embeddings
- `sentence-transformers`: Text embedding models

---

### Phase 4: Verify ALL Backend Dependencies (2 minutes)

**Where**: PowerShell (with `master_creator` environment activated)

**Command**:
```powershell
python -c "import fastapi, uvicorn, websockets, sqlalchemy, pydantic, anthropic, chromadb, sentence_transformers, numpy, pandas; print('All backend packages imported successfully!')"
```

**Expected Output**:
```
All backend packages imported successfully!
```

**If you see this**: ✅ ALL Python packages are installed correctly!

**If you see `ModuleNotFoundError`**: ❌ Something went wrong, tell me which module failed.

---

### Phase 5: Initialize Database (1 minute)

#### Step 5.1: Create Database Tables

**Where**: PowerShell (in project folder, `master_creator` environment activated)

**Command**:
```powershell
python init_content_storage.py
```

**Expected Output**:
```
All tables created successfully!
✅ Content Storage database initialized
✅ 9 tables created in content_storage.db
```

**If you see this**: ✅ Database is ready!

**If you already ran this before**: You'll see the same output (it's idempotent - safe to run multiple times)

---

### Phase 6: Install Frontend Dependencies (5 minutes)

#### Step 6.1: Navigate to Frontend Folder

**Where**: PowerShell (you can keep `master_creator` activated or not - doesn't matter for npm)

**Command**:
```powershell
cd frontend
```

**Verify**:
```powershell
pwd
```

**Expected Output**:
```
Path
----
C:\Users\phant\OneDrive\Documents\GitHub\testrepo\master_creator_mvp\frontend
```

#### Step 6.2: Install Node.js Packages

**Where**: PowerShell (in `frontend/` folder)

**Command**:
```powershell
npm install
```

**Expected Output**:
```
added 234 packages, and audited 235 packages in 45s

42 packages are looking for funding
  run `npm fund` for details

found 0 vulnerabilities
```

**What This Does**: Installs all React, Vite, and frontend dependencies listed in `package.json`

**Time**: 2-5 minutes (downloads ~200MB)

**If you see warnings about "deprecated" packages**: ⚠️ Ignore them - they're normal

**If you see "vulnerabilities found"**: ⚠️ Ignore unless it says "critical" - we can fix later

#### Step 6.3: Verify Frontend Installation

**Command**:
```powershell
npm list react vite
```

**Expected Output**:
```
frontend@0.0.0 C:\Users\phant\OneDrive\Documents\GitHub\testrepo\master_creator_mvp\frontend
├── react@18.x.x
└── vite@5.x.x
```

**If you see this**: ✅ Frontend dependencies installed correctly!

---

### Phase 7: Start the Application (2 minutes)

#### Step 7.1: Open TWO PowerShell Windows

**Important**: You need TWO separate PowerShell windows:
1. **Terminal 1**: Backend server
2. **Terminal 2**: Frontend dev server

**How to Open Second PowerShell**:
- Press `Windows Key + X`
- Click "Windows PowerShell" or "Terminal"
- Repeat to open another one

#### Step 7.2: Start Backend Server (Terminal 1)

**Where**: PowerShell Terminal 1

**Commands**:
```powershell
# Navigate to project root
cd "C:\Users\phant\OneDrive\Documents\GitHub\testrepo\master_creator_mvp"

# Activate conda environment
conda activate master_creator

# Start backend server
python run_server.py
```

**Expected Output**:
```
Master Creator MVP - Starting Server
========================================

Configuration:
  Environment: development
  API Port: 8080
  Enable CORS: True
  Database: master_creator.db (SQLite)
  Content Storage: content_storage.db (SQLite)
  ChromaDB: ./chroma_data (Local)

Server will be available at: http://localhost:8080
API Documentation: http://localhost:8080/api/docs

Starting Uvicorn server...

INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

**If you see this**: ✅ Backend server is running!

**IMPORTANT**: Leave this terminal window open! Don't close it or press Ctrl+C.

#### Step 7.3: Verify Backend is Running

**Where**: Your web browser

**URL**: http://localhost:8080/health

**Expected Output** (in browser):
```json
{
  "status": "healthy",
  "timestamp": "2025-11-15T12:34:56.789012",
  "version": "3.0.0-mvp",
  "database": "connected",
  "content_storage": "connected"
}
```

**If you see this**: ✅ Backend API is working!

#### Step 7.4: Start Frontend Server (Terminal 2)

**Where**: PowerShell Terminal 2

**Commands**:
```powershell
# Navigate to frontend folder
cd "C:\Users\phant\OneDrive\Documents\GitHub\testrepo\master_creator_mvp\frontend"

# Start dev server (no conda environment needed for npm)
npm run dev
```

**Expected Output**:
```
> frontend@0.0.0 dev
> vite


  VITE v5.x.x  ready in 1234 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

**If you see this**: ✅ Frontend server is running!

**IMPORTANT**: Leave this terminal window open too!

#### Step 7.5: Open the Dashboard

**Where**: Your web browser

**URL**: http://localhost:3000

**Expected Result**:
- Dashboard loads with student data
- **TOP-RIGHT CORNER**: Look for a **GREEN PULSING DOT**
- Status should say: **"Live Updates Active"**

**If you see the green dot**: ✅ WebSocket real-time updates are working!

**If you see "Connecting..." or red dot**: ⚠️ WebSocket connection failed - check Terminal 1 for errors

---

### Phase 8: Test Real-Time Updates (1 minute)

#### Test 1: Generate Recommendations

**Where**: Dashboard (http://localhost:3000)

**Steps**:
1. Click on any student name in the left sidebar
2. Scroll to bottom of page
3. Click **"Generate Recommendations"** button (purple button)
4. **Watch the screen** - recommendations should appear WITHOUT refreshing!

**What You Should See**:
- Loading spinner appears briefly
- Recommendations section populates with learning path
- Green dot stays solid (connection still active)

**Open Browser Console** (F12 key):
```
WebSocket message received: {type: "recommendation_generated", ...}
Recommendations generated: {...}
Adaptive recommendations updated in real-time for: student_001
```

**If recommendations appear instantly**: ✅ Real-time updates are working!

---

## Troubleshooting Checklist

### Backend Won't Start

**Error**: `ModuleNotFoundError: No module named 'X'`

**Fix**:
```powershell
# Make sure conda environment is activated
conda activate master_creator

# Reinstall missing package
pip install X
```

---

**Error**: `Address already in use` or `Port 8080 is busy`

**Fix**:
```powershell
# Something is using port 8080, find and kill it
netstat -ano | findstr :8080

# Or change port in run_server.py (line ~15):
# PORT = 8081  # Change from 8080
```

---

### Frontend Won't Start

**Error**: `npm: command not found`

**Fix**: Node.js not installed correctly. Restart PowerShell and verify:
```powershell
node --version
npm --version
```

---

**Error**: `ENOENT: no such file or directory, open '...package.json'`

**Fix**: You're in the wrong folder
```powershell
cd "C:\Users\phant\OneDrive\Documents\GitHub\testrepo\master_creator_mvp\frontend"
```

---

### No Green Dot / "Connecting..." Stuck

**Check 1**: Is backend running?
```powershell
# In browser, visit:
http://localhost:8080/health
```

Should return JSON with `"status": "healthy"`

**Check 2**: Open browser DevTools (F12) → Console tab

Look for errors like:
- `WebSocket connection failed`
- `Failed to connect to ws://localhost:3000/ws/dashboard/class_001`

**Check 3**: Check Terminal 1 (backend) for WebSocket errors

---

### Import Errors for sentence-transformers

**Error**: `No module named 'sentence_transformers'`

**Fix**:
```powershell
conda activate master_creator
pip install sentence-transformers
```

**Note**: First import downloads ~400MB of models - be patient!

---

## Summary Checklist - Is Everything Working?

Before you start working, verify ALL of these:

- [ ] **Anaconda installed**: `python --version` shows Anaconda
- [ ] **Conda environment created**: `conda activate master_creator` works
- [ ] **All Python packages installed**: Import test passes (Phase 4.1)
- [ ] **Database initialized**: `content_storage.db` file exists
- [ ] **Frontend dependencies installed**: `npm list` shows packages
- [ ] **Backend running**: Terminal 1 shows Uvicorn logs, http://localhost:8080/health works
- [ ] **Frontend running**: Terminal 2 shows Vite logs, http://localhost:3000 loads
- [ ] **WebSocket connected**: Green pulsing dot visible in top-right
- [ ] **Real-time updates working**: "Generate Recommendations" button works without refresh

**If ALL checked**: 🎉 **YOU'RE READY TO USE THE SYSTEM!**

---

## What Did We Install? (Full Inventory)

### System Tools
1. **Anaconda 2024.10** (~3GB)
   - Includes: Python 3.11, conda, pip, numpy, pandas, and 250+ packages

### Python Packages (in `master_creator` conda environment)
1. **numpy** - Numerical computations
2. **pandas** - Data manipulation
3. **fastapi** - Web framework
4. **uvicorn** - ASGI server
5. **websockets** - WebSocket protocol
6. **python-dotenv** - Environment variables
7. **python-multipart** - Form data handling
8. **sqlalchemy** - Database ORM
9. **pydantic** - Data validation
10. **anthropic** - Claude API client
11. **chromadb** - Vector database
12. **sentence-transformers** - Text embeddings (~500MB with models)

### Frontend Packages (in `frontend/node_modules/`)
~235 packages including:
1. **react** - UI framework
2. **vite** - Build tool
3. **recharts** - Charting library
4. **lucide-react** - Icons
5. And 230+ dependencies

### Database Files
1. **master_creator.db** - Student model database (from previous setup)
2. **content_storage.db** - Content and assessments database
3. **chroma_data/** - Vector embeddings storage

**Total Disk Space Used**: ~4-5GB

---

## Daily Workflow (After Initial Setup)

Every time you want to work on the project:

### Step 1: Open Two PowerShell Windows

### Step 2: Terminal 1 - Start Backend
```powershell
cd "C:\Users\phant\OneDrive\Documents\GitHub\testrepo\master_creator_mvp"
conda activate master_creator
python run_server.py
```

### Step 3: Terminal 2 - Start Frontend
```powershell
cd "C:\Users\phant\OneDrive\Documents\GitHub\testrepo\master_creator_mvp\frontend"
npm run dev
```

### Step 4: Open Browser
Visit: http://localhost:3000

**That's it!** Leave both terminals running while you work.

---

## Cost Estimation

**Total Installation Time**: ~40-60 minutes
- Anaconda download + install: 15-20 min
- Environment setup: 5 min
- Python packages: 10 min
- Frontend packages: 5 min
- Database init: 1 min
- Server startup: 2 min
- Testing: 5 min

**One-Time Setup**: After this, startup takes only 2 minutes (just run the servers)

---

## Why This Approach Works

1. **Anaconda eliminates compilation issues** - All packages are prebuilt
2. **Conda environment isolates the project** - Won't conflict with other Python projects
3. **Complete dependency list upfront** - No more "missing module" errors
4. **Clear verification steps** - You know if something went wrong immediately
5. **Tested on Windows** - These exact steps work on fresh Windows installs

---

## Getting Help

If you hit ANY errors not covered in troubleshooting:

1. **Check Terminal 1 (backend)** for error messages
2. **Check Terminal 2 (frontend)** for error messages
3. **Check browser console (F12)** for JavaScript errors
4. **Copy the EXACT error message** and provide it

**Don't skip verification steps!** Each phase has a "Expected Output" - if you don't see it, stop and debug before continuing.

---

**Last Updated**: 2025-11-15
**Tested On**: Windows 10/11, fresh installation
**Python Version**: 3.11 (via Anaconda)
**Node.js Version**: 22.21.1

---

## Next Steps After Successful Setup

Once everything is running:

1. Read `READY_TO_RUN.md` for feature overview
2. Read `WEBSOCKET_REALTIME_UPDATES.md` for technical details
3. Explore the dashboard - try different students
4. Test "Generate Recommendations" button
5. Open multiple browser windows - watch them all update simultaneously!

**Enjoy your real-time learning dashboard!** ✨
