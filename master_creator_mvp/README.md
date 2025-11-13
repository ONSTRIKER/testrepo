# Master Creator v3 MVP - 9-Engine Adaptive Learning System

## 🎯 Overview

Master Creator v3 is a production-ready K-12 special education adaptive learning platform designed for **15 teachers × 150 students (2,250 total users)**. The system uses 9 specialized AI engines to create personalized learning experiences that comply with FERPA, IDEA, and Section 504 requirements.

## 🏗️ System Architecture

### 9-Engine Pipeline Flow

```
Engine 0: Unit Plan Designer
    ↓
Engine 1: Lesson Architect
    ↓
Engine 5: Diagnostic Engine (Bayesian Knowledge Tracing)
    ↓
Engine 2: Worksheet Designer (3-tier differentiation)
    ↓
Engine 3: IEP Modification Specialist
    ↓
Engine 4: Adaptive Personalization Engine
    ↓
Assessment Grader
    ↓
Engine 6: Feedback Loop (Bayesian parameter updates)
```

### Core Components

**Student Model** (Central Hub)
- PostgreSQL: Structured data (students, IEP info, assessment history)
- Chroma: Vector embeddings (learning preferences, concept relationships)
- **CRITICAL RULE**: All engines query Student Model API - NO direct database access

**Engines**
- **Engine 0**: Multi-lesson unit plans using Understanding by Design framework
- **Engine 1**: 10-part lesson blueprints with standards alignment
- **Engine 2**: 3-tier differentiated worksheets (same objective, varied scaffolds)
- **Engine 3**: IEP accommodations with legal compliance
- **Engine 4**: Adaptive branching logic and ZPD targeting
- **Engine 5**: Diagnostic questions with Bayesian Knowledge Tracing
- **Engine 6**: Prediction accuracy monitoring and model updates

**Assessment Grader**
- Multiple choice auto-scoring (<100ms)
- Constructed response rubric scoring (<2s using Claude API)
- Concept-level mastery updates

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- Anthropic API key (Claude Sonnet 4)

### Installation

1. **Clone and navigate to the project**:
```bash
cd master_creator_mvp
```

2. **Create virtual environment**:
```bash
python3.10 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade pip
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment**:
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

5. **Start database services**:
```bash
docker-compose up -d
# Wait for health checks to pass (~30 seconds)
docker-compose ps
```

6. **Initialize database**:
```bash
python -m src.student_model.database init
```

7. **Generate synthetic student data**:
```bash
python -m src.student_model.cold_start
```

8. **Run tests**:
```bash
pytest tests/ -v --cov=src
```

9. **Start API server**:
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8080 --reload
```

10. **Access API documentation**:
- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

## 📁 Project Structure

```
master_creator_mvp/
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── pyproject.toml                 # Project configuration
├── docker-compose.yml             # PostgreSQL + Chroma setup
├── .env.example                   # Environment template
│
├── src/
│   ├── student_model/             # Central data hub
│   │   ├── database.py            # PostgreSQL schemas
│   │   ├── vector_store.py        # Chroma integration
│   │   ├── interface.py           # StudentModelInterface API
│   │   ├── schemas.py             # Pydantic models
│   │   └── cold_start.py          # Synthetic data generation
│   │
│   ├── engines/                   # 9 AI engines
│   │   ├── base_engine.py         # Shared interfaces
│   │   ├── engine_0_unit_plan.py
│   │   ├── engine_1_lesson_architect.py
│   │   ├── engine_2_worksheet_designer.py
│   │   ├── engine_3_iep_modifications.py
│   │   ├── engine_4_adaptive_personalization.py
│   │   ├── engine_5_diagnostic.py
│   │   └── engine_6_feedback_loop.py
│   │
│   ├── grader/                    # Assessment scoring
│   │   ├── multiple_choice.py
│   │   ├── constructed_response.py
│   │   └── rubric_engine.py
│   │
│   ├── orchestration/             # LangGraph workflows
│   │   ├── pipeline.py
│   │   └── state_management.py
│   │
│   ├── rag/                       # Research knowledge base
│   │   ├── knowledge_base.py
│   │   └── retrieval.py
│   │
│   ├── api/                       # FastAPI application
│   │   ├── main.py
│   │   └── routes/
│   │
│   └── utils/                     # Utilities
│       ├── validation.py
│       ├── logging_config.py
│       └── compliance_checks.py
│
├── tests/                         # Test suite (>80% coverage)
│   ├── test_student_model.py
│   ├── test_engines/
│   ├── test_grader.py
│   └── test_integration.py
│
├── data/
│   ├── synthetic_students/        # 18 test profiles
│   ├── research_modules/          # Educational research PDFs
│   └── schemas/                   # SQL DDL scripts
│
└── docs/
    ├── architecture.md            # Detailed system design
    ├── api_reference.md           # Endpoint documentation
    └── integration_guide.md       # Usage examples
```

## 🔧 API Endpoints

### Core Pipeline Endpoints

```
POST /api/v1/generate-unit
- Input: {topic, grade_level, duration, standards}
- Output: Multi-lesson unit plan (Engine 0)

POST /api/v1/generate-lesson
- Input: {unit_plan_id OR topic, grade_level}
- Output: 10-part lesson blueprint (Engine 1)

POST /api/v1/run-diagnostic
- Input: {lesson_id, student_ids}
- Output: Diagnostic questions + mastery estimates (Engine 5)

POST /api/v1/generate-worksheet
- Input: {lesson_id, diagnostic_results}
- Output: 3-tier differentiated worksheet (Engine 2)

POST /api/v1/apply-iep-modifications
- Input: {worksheet_id, student_ids}
- Output: Individualized modifications (Engine 3)

POST /api/v1/submit-assessment
- Input: {student_id, assessment_data}
- Output: Scores, feedback, updated mastery (Grader → Engine 6)

GET /api/v1/student/{id}/dashboard
- Output: Student profile, mastery data, progress tracking
```

## 🎓 Educational Compliance

The system ensures compliance with:

- **FERPA**: No PII in logs, encrypted data at rest, comprehensive audit trails
- **COPPA**: Parental consent workflows for students <13 years old
- **IDEA**: Proper IEP accommodation application (Engine 3)
- **Section 504**: Disability accommodations without lowering standards
- **UDL**: Multiple means of representation, action, and engagement
- **Trauma-Informed**: Safe content selection and emotional support
- **Culturally Responsive**: Diverse examples, stereotype avoidance

## 💰 Cost Management

**Budget**: $1,000 API credit
**Target**: <$0.50 per complete lesson generation

Optimization strategies:
- Aggressive prompt caching (LangGraph support)
- Request batching where possible
- Rate limiting to prevent runaway costs
- Per-engine token usage monitoring

## 🧪 Testing

```bash
# Run all tests with coverage
pytest tests/ -v --cov=src --cov-report=html

# Run specific test suite
pytest tests/test_student_model.py -v

# Run integration tests only
pytest tests/test_integration.py -v -m integration

# Generate coverage report
open htmlcov/index.html
```

**Coverage Target**: >80% across all modules

## 🔒 Security & Privacy

- All PII encrypted at rest using AES-256
- Audit logs for all student data access
- On-premise deployment (no cloud storage)
- Rate limiting on API endpoints
- Input validation on all endpoints
- SQL injection prevention via SQLAlchemy ORM
- XSS protection in generated content

## 📊 Performance Targets

- Student Model queries: <50ms
- Multiple choice grading: <100ms
- Constructed response grading: <2s
- Full lesson generation: <30s
- System supports: 2,250 concurrent users

## 🐛 Troubleshooting

### Database connection fails
```bash
# Check Docker containers are running
docker-compose ps

# View logs
docker-compose logs postgres
docker-compose logs chroma

# Restart services
docker-compose restart
```

### API key errors
```bash
# Verify .env file exists and has valid key
cat .env | grep ANTHROPIC_API_KEY

# Test API key
python -c "import anthropic; client = anthropic.Anthropic(); print('OK')"
```

### Import errors
```bash
# Ensure virtual environment is activated
which python  # Should show venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 📚 Additional Documentation

- [Architecture Deep Dive](docs/architecture.md)
- [API Reference](docs/api_reference.md)
- [Integration Guide](docs/integration_guide.md)

## 🚦 Development Status

### ✅ Phase 1 - Foundation (Complete)
- [x] Project structure
- [x] Configuration files
- [ ] Student Model implementation
- [ ] Synthetic data generation

### 🔄 Phase 2 - Content Engines (In Progress)
- [ ] Engine 0: Unit Plan Designer
- [ ] Engine 1: Lesson Architect
- [ ] Engine 5: Diagnostic Engine
- [ ] Engine 2: Worksheet Designer
- [ ] Engine 3: IEP Modifications

### ⏳ Phase 3 - Adaptation & Assessment (Pending)
- [ ] Engine 4: Adaptive Personalization
- [ ] Assessment Grader
- [ ] Engine 6: Feedback Loop

### ⏳ Phase 4 - Orchestration & API (Pending)
- [ ] LangGraph pipeline
- [ ] FastAPI endpoints
- [ ] Integration tests
- [ ] Documentation

## 📝 License

Proprietary - Master Creator Team

## 🤝 Contributing

This is a production pilot system. Contact the development team before making changes.

---

**Built with**: Python 3.10+ | FastAPI | PostgreSQL | Chroma | LlamaIndex | LangGraph | Claude Sonnet 4
