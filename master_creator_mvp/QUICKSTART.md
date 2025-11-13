# Master Creator v3 MVP - Quickstart Guide

Get the Master Creator v3 system running on your local machine in minutes.

## Prerequisites

- **Python 3.11+** (3.11 recommended)
- **PostgreSQL 14+** (for student data storage)
- **Anthropic API Key** (Claude Sonnet 4 access)
- **Git** (to clone the repository)

## Step 1: Clone Repository

```bash
# Clone the repository
git clone <repository-url>
cd master_creator_mvp

# Or if already cloned, navigate to the directory
cd master_creator_mvp
```

## Step 2: Environment Setup

### Create Virtual Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

## Step 3: Database Setup

### Option A: Docker PostgreSQL (Recommended)

```bash
# Start PostgreSQL in Docker
docker run -d \
  --name master-creator-db \
  -e POSTGRES_USER=master_creator \
  -e POSTGRES_PASSWORD=your_secure_password \
  -e POSTGRES_DB=master_creator_db \
  -p 5432:5432 \
  postgres:15
```

### Option B: Local PostgreSQL

```bash
# Install PostgreSQL (macOS with Homebrew)
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb master_creator_db
```

### Initialize Database Schema

```bash
# Run database migrations
python scripts/init_database.py
```

## Step 4: Configuration

### Create `.env` File

Create a `.env` file in the project root:

```bash
# Copy example environment file
cp .env.example .env
```

### Edit `.env` with Your Settings

```env
# Claude API
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# Database
DATABASE_URL=postgresql://master_creator:your_secure_password@localhost:5432/master_creator_db

# Chroma Vector Database
CHROMA_PERSIST_DIRECTORY=./chroma_data

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO

# Security
SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-hex-32

# Cost Tracking
ENABLE_COST_TRACKING=true
COST_PER_MILLION_INPUT_TOKENS=3.0
COST_PER_MILLION_OUTPUT_TOKENS=15.0
```

### Get Your Anthropic API Key

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy and paste into `.env` file

## Step 5: Load Cold Start Data

Import the 18 synthetic student profiles:

```bash
# Preview what will be imported (dry run)
python scripts/import_cold_start_data.py --dry-run

# Actually import the data
python scripts/import_cold_start_data.py
```

This creates:
- 18 student profiles
- 6 IEP records with accommodations
- 90 initial mastery estimates (5 concepts × 18 students)

## Step 6: Start the Server

### Option A: Development Server (FastAPI)

```bash
# Start FastAPI development server
cd src
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at: **http://localhost:8000**

### Option B: Production Server (with Gunicorn)

```bash
# Start production server
cd src
gunicorn api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

## Step 7: Verify Installation

### Check API Health

Open your browser or use curl:

```bash
# Check if API is running
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "version": "1.0.0"}
```

### View API Documentation

Open in browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Step 8: Try Your First Lesson

### Using the API (curl)

```bash
curl -X POST http://localhost:8000/api/lessons/lessons \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Photosynthesis",
    "grade_level": "9",
    "subject": "Science",
    "duration_minutes": 45,
    "standards": ["NGSS-HS-LS1-5"]
  }'
```

### Using Python

```python
import requests

# Generate a lesson
response = requests.post(
    "http://localhost:8000/api/lessons/lessons",
    json={
        "topic": "Photosynthesis",
        "grade_level": "9",
        "subject": "Science",
        "duration_minutes": 45,
        "standards": ["NGSS-HS-LS1-5"]
    }
)

lesson = response.json()
print(f"Lesson ID: {lesson['lesson_id']}")
print(f"Cost: ${lesson['cost_summary']['total_cost']:.4f}")
print(f"Sections: {len(lesson['sections'])}")
```

### Using the Interactive Docs

1. Go to http://localhost:8000/docs
2. Find `POST /api/lessons/lessons`
3. Click "Try it out"
4. Enter the request body
5. Click "Execute"
6. View the response

## Step 9: Run Complete Pipeline

Generate lesson + diagnostic + worksheets + IEP modifications:

```bash
curl -X POST http://localhost:8000/api/pipeline/run \
  -H "Content-Type: application/json" \
  -d '{
    "lesson_topic": "Photosynthesis",
    "grade_level": "9",
    "subject": "Science",
    "class_id": "class_bio_101_cold_start",
    "concept_ids": ["photosynthesis_process"],
    "duration_minutes": 45,
    "standards": ["NGSS-HS-LS1-5"],
    "num_questions_per_concept": 3,
    "execution_mode": "synchronous"
  }'
```

This runs:
1. **Engine 1**: Generate lesson plan
2. **Engine 5**: Generate diagnostic assessment
3. **Engine 2**: Generate 3-tier differentiated worksheets
4. **Engine 3**: Apply IEP accommodations

## Available Endpoints

### Lesson Generation
- `POST /api/lessons/units` - Generate unit plan (Engine 0)
- `POST /api/lessons/lessons` - Generate lesson (Engine 1)

### Student Management
- `POST /api/students/` - Create student profile
- `GET /api/students/{student_id}` - Get student profile
- `GET /api/students/class/{class_id}` - Get class roster
- `POST /api/students/{student_id}/iep` - Create IEP
- `GET /api/students/{student_id}/mastery/{concept_id}` - Get mastery estimate

### Assessments & Worksheets
- `POST /api/worksheets/generate` - Generate worksheets (Engine 2)
- `POST /api/worksheets/apply-iep` - Apply IEP modifications (Engine 3)
- `POST /api/assessments/submit` - Submit assessment responses
- `POST /api/assessments/batch-grade` - Grade batch of responses

### Pipeline Orchestration
- `POST /api/pipeline/run` - Run complete pipeline
  - Modes: `synchronous`, `asynchronous`, `langgraph`

### Adaptive Personalization
- `POST /api/adaptive/plan` - Generate adaptive plan (Engine 4)
- `POST /api/adaptive/feedback` - Get feedback analysis (Engine 6)

## Troubleshooting

### Database Connection Error

```
Error: could not connect to server: Connection refused
```

**Solution**: Make sure PostgreSQL is running
```bash
# Check if PostgreSQL is running
docker ps | grep master-creator-db

# Or for local installation
pg_isready
```

### API Key Error

```
Error: Invalid API key
```

**Solution**: Check your `.env` file
- Make sure `ANTHROPIC_API_KEY` is set correctly
- No quotes around the key
- No extra spaces

### Module Not Found Error

```
ModuleNotFoundError: No module named 'anthropic'
```

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Port Already in Use

```
Error: Address already in use
```

**Solution**: Use a different port
```bash
uvicorn api.main:app --port 8001
```

## Cost Estimation

With Claude Sonnet 4 pricing:
- **Input**: $3.00 per million tokens
- **Output**: $15.00 per million tokens

Typical costs per lesson:
- **Simple lesson** (no worksheets): $0.05 - $0.15
- **Complete pipeline** (lesson + diagnostic + 3 worksheets + IEP): $0.30 - $0.50

## Testing

### Run Tests

```bash
# Run all tests
pytest

# Run integration tests only
pytest tests/test_integration.py -v

# Run with coverage
pytest --cov=src --cov-report=html
```

### Test with Cold Start Data

The 18 student profiles in `data/cold_start_students.json` can be used for testing:
- Different tier levels (1, 2, 3)
- Various IEP accommodations
- Realistic mastery distributions

## Next Steps

1. **Explore the API**: Use the Swagger UI at http://localhost:8000/docs
2. **Generate Content**: Try different subjects and grade levels
3. **Test Differentiation**: See how worksheets vary by tier
4. **Review IEP Modifications**: Check how accommodations are applied
5. **Monitor Costs**: Track token usage and costs per request

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     Teacher UI                          │
│                   (React/TypeScript)                    │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST
┌────────────────────▼────────────────────────────────────┐
│                  FastAPI Server                         │
│                  (40+ endpoints)                        │
└────┬────────────────────────────────────────┬──────────┘
     │                                        │
     │ ┌──────────────────────────────────────▼──────┐
     │ │      LangGraph Orchestration               │
     │ │   (Async pipeline with state management)   │
     │ └──────────────────────────────────────────────┘
     │
┌────▼─────────────────────────────────────────────────────┐
│                   9 AI Engines                           │
│  Engine 0: Unit Plan Designer    Engine 1: Lesson       │
│  Engine 2: Worksheet Designer    Engine 3: IEP Specialist│
│  Engine 4: Adaptive Planner      Engine 5: Diagnostic   │
│  Engine 6: Feedback Loop         Assessment Grader      │
└────┬─────────────────────────────────────────┬──────────┘
     │                                         │
┌────▼────────────────────┐      ┌────────────▼──────────┐
│   Student Model API     │      │   Claude Sonnet 4     │
│  (NO direct DB access)  │      │   (Anthropic API)     │
└────┬────────────────────┘      └───────────────────────┘
     │
┌────▼────────────────────┐
│  PostgreSQL + Chroma    │
│  (Student data + RAG)   │
└─────────────────────────┘
```

## Support

- **Documentation**: See `/docs` folder for detailed guides
- **API Reference**: http://localhost:8000/docs
- **Test Data**: `data/cold_start_students.json`
- **Example Scripts**: `scripts/` folder

## Security Notes

⚠️ **Important for Production**:
1. Change default passwords in `.env`
2. Use environment variables, not hardcoded secrets
3. Enable HTTPS/TLS for API
4. Implement authentication/authorization
5. Regular security audits for student data (FERPA compliance)
6. Encrypt database at rest
7. Use secure API key storage (e.g., AWS Secrets Manager)

---

**You're all set!** 🎉 Start generating adaptive lessons for your students.
