# Master Creator v3 MVP - Teacher UI

## 🎓 Overview

Streamlit multi-page application providing teachers with a complete interface for adaptive lesson generation, differentiated worksheet management, student progress tracking, and IEP compliance.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd /path/to/master_creator_mvp
pip install -r requirements.txt
```

### 2. Run the Application

```bash
# From the teacher_ui directory
streamlit run Home.py

# Or from project root
streamlit run teacher_ui/Home.py
```

The application will open in your browser at `http://localhost:8501`

## 📁 Application Structure

```
teacher_ui/
├── Home.py                          # Landing page with quick actions
└── pages/
    ├── 1_Generate_Lesson.py         # Main workflow: Unit planner + lesson generator
    ├── 2_Review_Worksheets.py       # 3-tier differentiated worksheet review
    ├── 3_Student_Dashboard.py       # Student progress and mastery tracking
    ├── 4_IEP_Manager.py             # IEP accommodations management
    └── 5_Settings.py                # Roster import + system preferences
```

## 🎯 Page-by-Page Features

### Home Page
- Quick action buttons for common tasks
- System overview with metrics (2,250 students, 1,350 with IEPs)
- Recent activity feed
- Navigation sidebar

### Page 1: Generate Lesson
**Unit Planner (Optional - Engine 0)**
- Create 3-10 day multi-lesson units
- Standards alignment (NGSS, CCSS)
- Understanding by Design framework
- Click any lesson to auto-fill single lesson generator

**Lesson Generator (Engine 1)**
- Single lesson with 10-part structure
- Class roster selection (shows "18 students, 12 with IEPs")
- Standards alignment
- Triggers full pipeline: Engine 1 → Engine 5 → Engine 2+3

**Progress Tracking**
- Real-time indicators for each engine
- Lesson preview with inline editing
- Export to PDF/DOCX

### Page 2: Review Worksheets
**3-Tier Tab Interface**
- **Tier 1 (Light Support)**: 6 students, 75%+ mastery
- **Tier 2 (Moderate Support)**: 8 students, 45-75% mastery, IEP badges
- **Tier 3 (Heavy Support)**: 4 students, <45% mastery, full IEP details

**Per-Tier Features**
- Student lists with mastery percentages
- Question previews with scaffolding details
- IEP accommodations applied (e.g., "Extended time for 3 students")
- Reassign students between tiers
- Edit questions inline

**Export Options**
- Export all tiers as single PDF
- Print worksheets
- Email to students
- Continue to Student Dashboard

### Page 3: Student Dashboard
**Class Overview**
- Plotly bar chart: Mastery distribution by concept
- "Students Needing Attention" alerts (<50% mastery)
- Full roster table with IEP status, reading level, overall mastery

**Individual Student Profile**
- Concept-by-concept mastery breakdown (progress bars)
- Recent assessment history (worksheets, quizzes, diagnostics)
- Active IEP accommodations list
- Adaptive recommendations from Engine 4:
  - Tier change suggestions
  - Intervention needs
  - Strength areas

**Actions**
- Export student report (PDF)
- Email progress to parents
- Update IEP

### Page 4: IEP Manager
**Student List**
- All students with IEPs (currently 12 in demo)
- Primary/secondary disabilities
- Active accommodations with settings
- Review date tracking (30-day warnings)

**Edit IEP Modal**
- Disability category selection (IDEA compliant)
- 12 accommodation types with settings:
  - Extended Time (1.0x - 3.0x multiplier)
  - Text-to-Speech
  - Reduced Questions (10-50% reduction)
  - Graphic Organizers
  - Calculator, Scribe, etc.
- Modifications (alternate grading, reduced content)
- IEP goals (3 text areas)

**Add New Student**
- Manual entry form
- Quick accommodation setup
- Integration with full IEP workflow

**Compliance**
- IDEA, Section 504, FERPA badges
- All accommodations automatically applied by Engine 3

### Page 5: Settings
**Tab 1: CSV Bulk Import**
- Download template CSV
- Upload class roster
- Validation checks (required columns, IEP count, grade distribution)
- Assign to existing or new class
- Import summary with success/failure counts

**Tab 2: Manual Student Addition**
- Individual student form
- Academic profile (reading level, VARK learning preferences)
- IEP checkbox with quick accommodations

**Tab 3: System Preferences**
- **Lesson Defaults**: Duration, subject, grade
- **Tier Assignment Logic**: Automatic/Manual/Hybrid with mastery thresholds
- **Export Formats**: PDF, DOCX, Google Docs
- **Display**: Theme, date format, animations
- **Performance**: Prompt caching, cost limits ($0.50/lesson), rate limiting
- **Compliance**: FERPA audit logs, COPPA consent, data retention (365 days)

## 🎨 UI Features

- **Teacher-friendly styling**: Custom CSS for optimal readability
- **Session state**: Workflow continuity across pages
- **Mock data**: Fully functional without backend (18 students, 12 with IEPs)
- **Responsive design**: Optimized for 1366×768 teacher laptops
- **FERPA compliant**: No PII in URLs or logs
- **Progress indicators**: Loading states, success messages, animations
- **Contextual help**: Tooltips and info boxes throughout

## 📊 Mock Data

The UI includes comprehensive mock data demonstrating:

**Students (18 total)**
- Alex Chen, Jordan Rivera, Sam Parker (Tier 1, no IEP)
- Maria Gonzalez (Learning Disability, Tier 2)
- Carlos Martinez (Speech/Language, Tier 2)
- David Kim (ADHD, Tier 3)
- Emma Wilson (Learning Disability, Tier 3)
- ... and 11 more

**Concepts with Mastery Data**
- Photosynthesis: 72% mean, 6 students <50%
- Cell Structure: 61% mean, 6 students <50%
- Genetics: 38% mean, 11 students <50%
- Evolution: 55% mean, 7 students <50%

**IEP Accommodations (12 types)**
- Extended Time, Text-to-Speech, Reduced Questions
- Graphic Organizers, Calculator, Scribe
- Preferential Seating, Movement Breaks
- Sentence Frames, Word Bank, Visual Supports, Audio Recordings

## 🔌 Backend Integration Points

The UI has TODO markers for these API endpoints:

```python
# Lesson Generation
POST /api/v1/generate-unit
POST /api/v1/generate-lesson
POST /api/v1/run-diagnostic
POST /api/v1/generate-worksheet

# Worksheets
GET  /api/v1/worksheet/{id}
PUT  /api/v1/worksheet/{id}
POST /api/v1/worksheet/export

# Student Data
GET  /api/v1/classes/{id}/roster
GET  /api/v1/students/{id}/profile
GET  /api/v1/students/{id}/mastery
GET  /api/v1/students/{id}/dashboard

# IEP Management
GET  /api/v1/students/{id}/iep
PUT  /api/v1/students/{id}/iep
POST /api/v1/students/import

# Settings
GET  /api/v1/settings
PUT  /api/v1/settings
```

## 🎯 Teacher Workflow

1. **Import Roster** (Page 5)
   - Upload CSV or manually add students
   
2. **Set Up IEPs** (Page 4)
   - Configure accommodations for students with IEPs
   
3. **Generate Lesson** (Page 1)
   - Optional: Create multi-lesson unit
   - Generate single lesson with standards
   - Select class roster
   - System runs Engine 1 → 5 → 2 → 3
   
4. **Review Worksheets** (Page 2)
   - Check 3-tier differentiated materials
   - Verify IEP accommodations applied
   - Edit questions if needed
   - Export for distribution
   
5. **Monitor Progress** (Page 3)
   - View class mastery distribution
   - Check individual student profiles
   - Identify students needing attention
   - Read adaptive recommendations

## 🐛 Troubleshooting

### Streamlit won't start
```bash
# Ensure you're in the right directory
cd teacher_ui

# Check if streamlit is installed
pip list | grep streamlit

# Reinstall if needed
pip install streamlit==1.29.0
```

### Port already in use
```bash
# Specify a different port
streamlit run Home.py --server.port 8502
```

### Missing dependencies
```bash
# Install all required packages
pip install -r ../requirements.txt
```

## 📝 Notes

- **Current State**: Fully functional UI with mock data
- **Backend**: Not yet implemented (APIs return mock responses)
- **Next Steps**: Build Student Model, implement engines, connect FastAPI
- **Testing**: Click through all pages to see complete workflow

## 🚦 Development Status

- ✅ Home page with quick actions
- ✅ Page 1: Lesson Generator (Unit Planner + Lesson Architect)
- ✅ Page 2: Worksheet Review (3-tier tabs)
- ✅ Page 3: Student Dashboard (mastery tracking)
- ✅ Page 4: IEP Manager (accommodation settings)
- ✅ Page 5: Settings (CSV import + preferences)
- ⏳ Backend API integration (pending)
- ⏳ Real data from Student Model (pending)
- ⏳ Engine implementations (pending)

## 📚 Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Charts](https://plotly.com/python/)
- [Master Creator Architecture](../docs/architecture.md)
- [API Reference](../docs/api_reference.md)

---

**Built with**: Streamlit 1.29.0 | Plotly 5.18.0 | Python 3.10+
