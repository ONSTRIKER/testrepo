# Master Creator v3 MVP - AI-Powered Adaptive Learning System

## 🎯 Project Overview

**Master Creator v3 MVP** is an AI-powered adaptive learning system for K-12 special education, designed to generate personalized educational content using Claude AI. The system currently supports lesson generation with planned expansion to a full 9-engine pipeline.

**Current Status**: ✅ **Working and Deployed** - Lesson generation operational on Windows

---

## ✨ What's Working Right Now

### ✅ Operational Features
- **Lesson Generation (Engine 1)**: AI-powered 10-part lesson blueprints using Claude Sonnet 4
- **FastAPI Backend**: RESTful API with interactive Swagger documentation
- **SQLite Database**: Local data storage for student profiles and assessments
- **Cost Tracking**: Per-request token usage and cost monitoring
- **Windows Compatible**: Fully tested and working on Windows 10/11

### 🚧 In Development
- Unit Plan Designer (Engine 0)
- Worksheet Designer (Engine 2) - 3-tier differentiation
- IEP Specialist (Engine 3)
- Diagnostic Engine (Engine 5) - Bayesian Knowledge Tracing
- Adaptive Engine (Engine 4)
- Feedback Loop (Engine 6)
- Student Dashboard UI
- Assessment Grading

---

## 🏗️ Current Architecture

```
User Request
    ↓
FastAPI Backend (Python 3.10+)
    ↓
Engine 1: Lesson Architect
    ↓
Claude Sonnet 4 API (Anthropic)
    ↓
JSON Lesson Blueprint
    ↓
Response to User
```

### Technology Stack

- **Backend**: FastAPI + Python 3.10+
- **AI Model**: Claude Sonnet 4 (via Anthropic API)
- **Database**: SQLite (production will use PostgreSQL)
- **API Documentation**: Swagger UI (auto-generated)
- **Optional Dependencies**:
  - ChromaDB (vector store) - not required for basic operation
  - LangGraph (advanced workflows) - not required for basic operation

---

## 🚀 Quick Start (Windows)

### Prerequisites

- **Python 3.10 or higher** ([Download](https://www.python.org/downloads/))
- **Git** or **GitHub Desktop** ([Download](https://desktop.github.com/))
- **Anthropic API Key** ([Get one here](https://console.anthropic.com/))

### Installation Steps

1. **Clone the Repository**

   Using GitHub Desktop:
   - Open GitHub Desktop
   - Clone `ONSTRIKER/testrepo`
   - Navigate to branch: `claude/master-creator-mvp-setup-011CV5C3xffNS1PVQPuYpxAj`

2. **Navigate to Project Directory**

   ```powershell
   cd C:\Users\YourName\Documents\GitHub\testrepo\master_creator_mvp
   ```

3. **Run Automated Setup**

   Double-click `setup_windows.bat` or run in PowerShell:
   ```powershell
   .\setup_windows.bat
   ```

   This will:
   - Create a Python virtual environment
   - Install all required packages
   - Set up the project structure

4. **Configure API Key**

   - Open `.env` in Notepad (enable "Show hidden files" if you can't see it)
   - Find line: `ANTHROPIC_API_KEY=your_anthropic_api_key_here`
   - Replace with your actual API key: `ANTHROPIC_API_KEY=sk-ant-api03-...`
   - Save the file

5. **Start the Server**

   Double-click `start_server.bat` or run:
   ```powershell
   .\start_server.bat
   ```

   You should see:
   ```
   DATABASE_URL: sqlite:///./master_creator.db
   Starting FastAPI server...
   Server will be available at: http://localhost:8080
   INFO:     Application startup complete.
   ```

6. **Access the API**

   Open your browser and go to: **http://localhost:8080/api/docs**

---

## 📖 Using the API

### Generate a Lesson

1. Go to http://localhost:8080/api/docs
2. Find **POST /api/lessons/lessons**
3. Click **"Try it out"**
4. Use this example request:

```json
{
  "topic": "Photosynthesis",
  "grade_level": "9",
  "subject": "Biology",
  "duration_minutes": 45,
  "standards": ["MS-LS1-6"]
}
```

5. Click **"Execute"**
6. Wait ~1-2 minutes for Claude to generate the lesson
7. View the complete lesson blueprint in the response

### Example Response

```json
{
  "status": "success",
  "lesson": {
    "lesson_id": "lesson_abc123",
    "topic": "Photosynthesis",
    "grade_level": "9",
    "subject": "Biology",
    "duration_minutes": 45,
    "standards": ["MS-LS1-6"],
    "sections": [
      {
        "section_number": 1,
        "section_name": "Opening / Hook",
        "duration_minutes": 5,
        "content": "...",
        "teacher_notes": "..."
      }
      // ... 9 more sections
    ]
  },
  "cost": {
    "total_input_tokens": 480,
    "total_output_tokens": 4096,
    "total_cost": 0.0629
  }
}
```

**Cost**: ~$0.06 per lesson generation

---

## 🗂️ Project Structure

```
master_creator_mvp/
├── src/
│   ├── api/                           # FastAPI application
│   │   ├── main.py                    # App entry point
│   │   └── routes/                    # API endpoints
│   │       ├── lessons.py             # Lesson generation
│   │       ├── students.py            # Student management
│   │       ├── worksheets.py          # Worksheet generation
│   │       ├── assessments.py         # Assessment grading
│   │       └── pipeline.py            # Pipeline orchestration
│   │
│   ├── engines/                       # AI Engines
│   │   ├── base_engine.py             # Base class for all engines
│   │   ├── engine_0_unit_planner.py   # Unit plan generation
│   │   ├── engine_1_lesson_architect.py  # ✅ Lesson generation (WORKING)
│   │   ├── engine_2_worksheet_designer.py
│   │   ├── engine_3_iep_specialist.py
│   │   ├── engine_4_adaptive.py
│   │   ├── engine_5_diagnostic.py
│   │   └── engine_6_feedback.py
│   │
│   ├── student_model/                 # Student data management
│   │   ├── database.py                # SQLAlchemy models
│   │   ├── interface.py               # Student Model API
│   │   ├── schemas.py                 # Pydantic models
│   │   └── vector_store.py            # ChromaDB integration (optional)
│   │
│   ├── orchestration/                 # Workflow management
│   │   ├── pipeline.py                # Basic pipeline
│   │   └── langgraph_pipeline.py      # Advanced workflows (optional)
│   │
│   ├── grader/                        # Assessment grading
│   │   ├── multiple_choice.py
│   │   ├── constructed_response.py
│   │   └── rubric_engine.py
│   │
│   └── utils/                         # Utilities
│       ├── logging_config.py
│       └── validation.py
│
├── tests/                             # Test suite
│   ├── test_engines/                  # Engine tests
│   └── test_integration.py            # Integration tests
│
├── data/                              # Sample data
│   └── cold_start/                    # Initial student data
│
├── scripts/                           # Utility scripts
│   ├── init_database.py               # Database initialization
│   └── generate_cold_start_data.py    # Sample data generation
│
├── .env                               # Environment configuration
├── .env.example                       # Example configuration
├── requirements.txt                   # Python dependencies
│
├── setup_windows.bat                  # ✅ Automated Windows setup
├── start_server.bat                   # ✅ Start the server
├── init_database.bat                  # Initialize database tables
└── install_missing_packages.bat       # Install additional packages
```

---

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# API Keys
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# Database (SQLite for local, PostgreSQL for production)
DATABASE_URL=sqlite:///./master_creator.db

# Vector Store (optional - ChromaDB)
CHROMA_PERSIST_DIRECTORY=./chroma_data

# Application Settings
APP_ENV=development
API_HOST=0.0.0.0
API_PORT=8080
LOG_LEVEL=INFO

# LLM Configuration
LLM_MODEL=claude-sonnet-4-5-20250929
LLM_MAX_TOKENS=4096
LLM_TEMPERATURE=0.7
ENABLE_PROMPT_CACHING=true

# Cost Management
MAX_COST_PER_REQUEST=1.00
DAILY_BUDGET_LIMIT=50.00
```

---

## 🔧 Optional Setup

### Initialize Database (for full features)

To use student profiles, classes, and assessment tracking:

1. Pull latest changes from GitHub
2. Run `init_database.bat`
3. This creates all database tables in SQLite

### Install Additional Packages

Some advanced features require additional packages:

```powershell
# ChromaDB (vector search for student learning profiles)
pip install chromadb

# LangGraph (advanced workflow orchestration)
pip install langgraph
```

**Note**: These are optional. Basic lesson generation works without them.

---

## 📊 API Endpoints

### Lessons
- `POST /api/lessons/lessons` - Generate a lesson ✅ **WORKING**
- `POST /api/lessons/units` - Generate a unit plan (in development)
- `GET /api/lessons/lessons/{id}` - Retrieve lesson (not implemented)

### Students
- `POST /api/students/students` - Create student profile
- `GET /api/students/students/{id}` - Get student data
- `POST /api/students/classes/{class_id}/bulk-import` - Import student roster

### Worksheets
- `POST /api/worksheets/generate` - Generate 3-tier worksheet (in development)

### Assessments
- `POST /api/assessments/grade` - Grade student work (in development)

### Pipeline
- `POST /api/pipeline/run` - Run full 9-engine pipeline (in development)

Full API documentation: http://localhost:8080/api/docs

---

## 🧪 Testing

### Run Tests

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run all tests
pytest

# Run specific test file
pytest tests/test_engines/test_engine_1.py

# Run with coverage
pytest --cov=src tests/
```

### Manual Testing via Swagger UI

1. Start the server: `.\start_server.bat`
2. Open: http://localhost:8080/api/docs
3. Try each endpoint with example data
4. Check responses and logs

---

## 🐛 Troubleshooting

### Server Won't Start

**Problem**: `ModuleNotFoundError: No module named 'X'`

**Solution**: Install missing package
```powershell
.\venv\Scripts\Activate.ps1
pip install package-name
```

---

**Problem**: `DATABASE_URL is set to PostgreSQL!`

**Solution**: Edit `.env` file and change to:
```
DATABASE_URL=sqlite:///./master_creator.db
```

---

**Problem**: `No such table: classes`

**Solution**: Initialize the database
```powershell
.\init_database.bat
```

---

### API Returns Errors

**Problem**: `500 Internal Server Error` or parsing errors

**Solution**: Check the server logs in PowerShell window. Look for error messages and stack traces.

---

**Problem**: `422 Unprocessable Entity`

**Solution**: Check your request body format. Make sure field names match the API schema (use `topic` not `lesson_topic`, etc.)

---

### Warnings (Safe to Ignore)

These warnings are normal and don't affect operation:

```
chromadb not available. Vector store features will be disabled.
langgraph not available. Advanced pipeline features will be disabled.
StudentVectorStore initialized without chromadb - vector features disabled
```

---

## 💰 Cost Estimation

### Per-Request Costs (Claude Sonnet 4)

| Operation | Input Tokens | Output Tokens | Cost |
|-----------|-------------|---------------|------|
| Generate Lesson | ~500 | ~4000 | $0.06 |
| Generate Unit Plan | ~800 | ~6000 | $0.10 |
| Generate Worksheet | ~600 | ~3000 | $0.05 |
| Grade Assessment | ~400 | ~500 | $0.01 |

**Daily Budget Recommendation**: $50/day = ~800 lesson generations

---

## 🔒 Security & Compliance

### Data Privacy
- All student data stored locally in SQLite
- No data sent to external services except Claude API
- API key stored in `.env` file (never commit to git)

### FERPA Compliance
- Audit logging for all student data access
- Anonymization available for demos
- Secure storage of PII

### Future Enhancements
- PostgreSQL with encryption at rest
- JWT authentication for API access
- Role-based access control (teacher, admin)

---

## 📈 Performance Metrics

Current performance (on typical Windows PC):

| Metric | Target | Current |
|--------|--------|---------|
| Lesson Generation | <60s | ~90s |
| API Response Time | <100ms | ~50ms |
| Server Startup | <10s | ~5s |

**Note**: First request may be slower due to model loading.

---

## 🚧 Roadmap

### Phase 1: Foundation (✅ Complete)
- [x] FastAPI backend setup
- [x] Claude API integration
- [x] Lesson generation (Engine 1)
- [x] Windows compatibility
- [x] Cost tracking
- [x] API documentation

### Phase 2: Core Engines (In Progress)
- [ ] Unit Plan Designer (Engine 0)
- [ ] Worksheet Designer (Engine 2)
- [ ] IEP Specialist (Engine 3)
- [ ] Diagnostic Engine (Engine 5)
- [ ] Assessment Grader

### Phase 3: Advanced Features
- [ ] Adaptive Engine (Engine 4)
- [ ] Feedback Loop (Engine 6)
- [ ] LangGraph pipeline orchestration
- [ ] Student dashboard UI
- [ ] Real-time progress tracking

### Phase 4: Production Ready
- [ ] PostgreSQL migration
- [ ] ChromaDB integration
- [ ] Authentication & authorization
- [ ] Multi-tenant support
- [ ] Production deployment (Docker, AWS)

---

## 🤝 Contributing

This project is currently in active development. For questions or issues:

1. Check existing documentation
2. Review server logs for error details
3. Test with example requests in Swagger UI

---

## 📚 Additional Resources

### Documentation
- **API Contracts**: See Swagger UI at http://localhost:8080/api/docs
- **Engine Design**: See `/src/engines/` for implementation details
- **Database Schema**: See `/src/student_model/database.py`

### External Resources
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

---

## 📝 Change Log

### Current Version (v0.2.0) - November 2025
- ✅ **Working lesson generation with Claude Sonnet 4**
- ✅ Windows-compatible setup scripts
- ✅ SQLite database support
- ✅ Optional ChromaDB and LangGraph
- ✅ Improved JSON parsing for Claude responses
- ✅ Cost tracking per request
- ✅ Interactive API documentation

### Previous Version (v0.1.0)
- Initial FastAPI setup
- Basic engine structure
- PostgreSQL schemas

---

## 🎯 Success Criteria

**Current Milestone**: ✅ **Achieved - Basic Lesson Generation Working**

**Demo Scenario**:
> Teacher needs a 45-minute 9th grade Biology lesson on photosynthesis.

**Result**:
> System generates complete 10-part lesson blueprint in ~90 seconds for $0.06.

**Next Milestone**: Full 9-engine pipeline with 3-tier differentiation

---

## 🆘 Getting Help

### Quick Fixes

**Server not starting?**
1. Make sure you ran `setup_windows.bat`
2. Check that `.env` has your API key
3. Verify `DATABASE_URL` is set to SQLite

**API errors?**
1. Check Swagger UI for correct request format
2. View server logs in PowerShell window
3. Make sure you're not including `class_id` (requires database init)

**Parsing errors?**
1. Pull latest changes (parser was recently improved)
2. Restart the server
3. Try generating a new lesson

---

**Built with ❤️ for K-12 special education teachers**

*Powered by Claude AI (Anthropic) | FastAPI | Python*
