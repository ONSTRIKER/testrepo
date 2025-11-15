# Quick Setup Checklist - Windows

**Use this checklist as you follow `WINDOWS_COMPLETE_SETUP.md`**

Print this out or keep it visible while installing!

---

## Phase 1: Install Anaconda ⏱️ 15 min

- [ ] Download Anaconda from https://www.anaconda.com/download/success (~600MB)
- [ ] Run installer
- [ ] ✅ CHECK: "Add Anaconda3 to my PATH environment variable"
- [ ] ✅ CHECK: "Register Anaconda3 as my default Python"
- [ ] Wait for installation to complete
- [ ] Close and reopen PowerShell
- [ ] Verify: `python --version` shows "Anaconda, Inc."
- [ ] Verify: `conda --version` shows version number

**If verification fails**: Restart computer and try again

---

## Phase 2: Create Project Environment ⏱️ 5 min

- [ ] Open PowerShell
- [ ] Navigate to project:
  ```powershell
  cd "C:\Users\phant\OneDrive\Documents\GitHub\testrepo\master_creator_mvp"
  ```
- [ ] Create environment:
  ```powershell
  conda create -n master_creator python=3.11 -y
  ```
- [ ] Activate environment:
  ```powershell
  conda activate master_creator
  ```
- [ ] Verify: Prompt shows `(master_creator)` at beginning

---

## Phase 3: Install Python Packages ⏱️ 10 min

**Keep environment activated for all of these!**

- [ ] Install numpy/pandas:
  ```powershell
  conda install numpy pandas -y
  ```
- [ ] Install web frameworks:
  ```powershell
  pip install fastapi uvicorn websockets python-dotenv python-multipart
  ```
- [ ] Install database tools:
  ```powershell
  pip install sqlalchemy pydantic
  ```
- [ ] Install AI/ML packages:
  ```powershell
  pip install anthropic chromadb sentence-transformers
  ```
  (This one takes 3-5 minutes - downloads models)

---

## Phase 4: Verify Backend ⏱️ 1 min

- [ ] Run verification command:
  ```powershell
  python -c "import fastapi, uvicorn, websockets, sqlalchemy, pydantic, anthropic, chromadb, sentence_transformers, numpy, pandas; print('All backend packages imported successfully!')"
  ```
- [ ] See: "All backend packages imported successfully!"

**If you see ModuleNotFoundError**: Go back to Phase 3 and reinstall that package

---

## Phase 5: Initialize Database ⏱️ 1 min

- [ ] Run database setup:
  ```powershell
  python init_content_storage.py
  ```
- [ ] See: "All tables created successfully!"

---

## Phase 6: Install Frontend ⏱️ 5 min

- [ ] Navigate to frontend:
  ```powershell
  cd frontend
  ```
- [ ] Install packages:
  ```powershell
  npm install
  ```
- [ ] Wait for completion (~2-5 minutes)
- [ ] See: "added 234 packages" (or similar)

---

## Phase 7: Start Servers ⏱️ 2 min

### Terminal 1 - Backend

- [ ] Open PowerShell
- [ ] Navigate to project:
  ```powershell
  cd "C:\Users\phant\OneDrive\Documents\GitHub\testrepo\master_creator_mvp"
  ```
- [ ] Activate environment:
  ```powershell
  conda activate master_creator
  ```
- [ ] Start server:
  ```powershell
  python run_server.py
  ```
- [ ] See: "Uvicorn running on http://0.0.0.0:8080"
- [ ] **LEAVE THIS WINDOW OPEN!**

### Terminal 2 - Frontend

- [ ] Open SECOND PowerShell window
- [ ] Navigate to frontend:
  ```powershell
  cd "C:\Users\phant\OneDrive\Documents\GitHub\testrepo\master_creator_mvp\frontend"
  ```
- [ ] Start dev server:
  ```powershell
  npm run dev
  ```
- [ ] See: "Local: http://localhost:3000/"
- [ ] **LEAVE THIS WINDOW OPEN TOO!**

---

## Phase 8: Verify Everything Works ⏱️ 2 min

### Check Backend

- [ ] Open browser
- [ ] Visit: http://localhost:8080/health
- [ ] See: JSON with `"status": "healthy"`

### Check Frontend

- [ ] Visit: http://localhost:3000
- [ ] Dashboard loads with student data
- [ ] **TOP-RIGHT CORNER**: See **GREEN PULSING DOT**
- [ ] Status says: "Live Updates Active"

### Test Real-Time Updates

- [ ] Click any student name (left sidebar)
- [ ] Scroll to bottom
- [ ] Click "Generate Recommendations" button (purple)
- [ ] **Recommendations appear WITHOUT page refresh!**

---

## 🎉 SUCCESS CRITERIA

All of these must be true:

✅ Anaconda installed (python --version shows Anaconda)
✅ Conda environment works (conda activate master_creator)
✅ All packages import successfully
✅ Database initialized (content_storage.db exists)
✅ Backend running (Terminal 1 shows logs)
✅ Frontend running (Terminal 2 shows logs)
✅ http://localhost:8080/health returns healthy
✅ http://localhost:3000 loads dashboard
✅ Green dot visible in top-right corner
✅ "Generate Recommendations" works instantly

**If ALL checked**: YOU'RE DONE! System is fully operational!

---

## Common Issues

### "pip not found" or "python not found"
→ Restart PowerShell after installing Anaconda
→ If still broken, restart computer

### "conda activate master_creator" doesn't work
→ Make sure you installed Anaconda and checked "Add to PATH"
→ Close and reopen PowerShell

### "Port 8080 already in use"
→ Something else is using port 8080
→ Kill that process or change port in run_server.py

### Green dot doesn't appear
→ Check Terminal 1 for errors
→ Press F12 in browser, check Console tab for errors
→ Make sure both backend AND frontend are running

### Recommendations don't appear instantly
→ Check browser console (F12) for WebSocket errors
→ Verify green dot is solid (not blinking red)

---

## Daily Startup (After First Install)

**Every time you want to work on the project:**

1. Open PowerShell #1:
   ```powershell
   cd "C:\Users\phant\OneDrive\Documents\GitHub\testrepo\master_creator_mvp"
   conda activate master_creator
   python run_server.py
   ```

2. Open PowerShell #2:
   ```powershell
   cd "C:\Users\phant\OneDrive\Documents\GitHub\testrepo\master_creator_mvp\frontend"
   npm run dev
   ```

3. Open browser → http://localhost:3000

**Total time**: 2 minutes

---

## Time Budget

**Total First-Time Setup**: 40-60 minutes
- Phase 1 (Anaconda): 15 min
- Phase 2 (Environment): 5 min
- Phase 3 (Packages): 10 min
- Phase 4 (Verify): 1 min
- Phase 5 (Database): 1 min
- Phase 6 (Frontend): 5 min
- Phase 7 (Servers): 2 min
- Phase 8 (Testing): 2 min

**Daily Startup After Setup**: 2 minutes

---

**Pro Tip**: Keep both PowerShell windows open while working. When you're done for the day, press Ctrl+C in each window to stop the servers.

**Need More Details?** See `WINDOWS_COMPLETE_SETUP.md` for full explanations and troubleshooting.
