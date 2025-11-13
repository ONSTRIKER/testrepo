# Cold Start Student Data

This directory contains synthetic student profiles for testing and demonstration of the Master Creator v3 MVP system.

## Files

- **`cold_start_students.json`**: 18 diverse student profiles with initial mastery estimates

## Student Distribution

### By Tier
- **Tier 1 (High Achievers)**: 4 students (22%)
  - Strong mastery across concepts (75-90%)
  - Minimal scaffolding needed

- **Tier 2 (On-Grade Level)**: 8 students (44%)
  - Moderate mastery (55-70%)
  - Benefits from differentiated instruction

- **Tier 3 (Intensive Support)**: 6 students (33%)
  - Lower mastery (35-55%)
  - Requires significant scaffolding

### By IEP Status
- **Non-IEP Students**: 12 (67%)
- **IEP Students**: 6 (33%)
  - Learning Disabilities: 2 students
  - ADHD: 1 student
  - Autism Spectrum Disorder: 1 student
  - Speech-Language Impairment: 1 student
  - Emotional Disturbance: 1 student

## Student Profiles

### Tier 1 Students (High Achievers)

1. **Emma Chen** - Advanced, above grade level reading
2. **Marcus Washington** - Strong analytical skills
3. **Sophia Rodriguez** - Excellent at connecting concepts
4. **James Kim** - Hands-on learner, excels in labs

### Tier 2 Students (On-Grade Level)

5. **Olivia Martinez** - Benefits from graphic organizers
6. **Liam Johnson** - Steady learner, needs repetition
7. **Ava Patel** - Strong work ethic
8. **Noah Thompson** - Reading challenges, strong concepts (Non-IEP)
9. **Isabella Garcia** - Collaborative learner
10. **Daniel Lee** - IEP (SLD), text-to-speech needed
11. **Aiden Taylor** - IEP (ADHD), needs movement breaks
12. **Jackson White** - IEP (Anxiety), bright but test-anxious

### Tier 3 Students (Intensive Support)

13. **Ethan Brown** - Needs significant scaffolding
14. **Mia Davis** - English learner, visual supports
15. **Alexander Wilson** - Benefits from hands-on activities
16. **Charlotte Anderson** - IEP (Autism), visual schedules
17. **Ryan Martinez** - IEP (Dysgraphia), scribe needed
18. **Grace Johnson** - IEP (Speech-Language), sentence frames

## Initial Mastery Estimates

Each student has initial Bayesian Knowledge Tracing (BKT) estimates for 5 core biology concepts:

- **photosynthesis_process**: Cell energy production
- **cellular_respiration**: Cellular metabolism
- **cell_structure**: Organelles and functions
- **dna_replication**: Genetic processes
- **ecosystems**: Environmental interactions

### BKT Parameters
- **mastery_probability**: Student's estimated mastery (0.0-1.0)
- **p_learn**: Learning rate (default 0.3)
- **p_guess**: Guess probability (default 0.25)
- **p_slip**: Slip probability (default 0.1)
- **num_observations**: 0 (cold start - no observations yet)

## Usage

### 1. Generate Cold Start Data

```bash
python scripts/generate_cold_start_data.py
```

This creates `cold_start_students.json` with 18 synthetic profiles.

### 2. Import into Database (Dry Run)

```bash
python scripts/import_cold_start_data.py --dry-run
```

Preview what will be imported without writing to database.

### 3. Import into Database

```bash
python scripts/import_cold_start_data.py
```

Populates database with:
- 18 student profiles
- 6 IEP records with accommodations
- 90 initial mastery estimates (18 students × 5 concepts)

### 4. Use in Tests

```python
import json

# Load cold start data
with open('data/cold_start_students.json', 'r') as f:
    data = json.load(f)

students = data['students']
class_id = data['class_id']

# Get IEP students
iep_students = [s for s in students if s['has_iep']]

# Get Tier 1 students
tier1_students = [s for s in students if s['tier_classification'] == 'tier_1']
```

## Accommodations Represented

The IEP students demonstrate all 12 accommodation types:

1. **EXTENDED_TIME** - Extra time on assessments
2. **TEXT_TO_SPEECH** - Audio reading of materials
3. **GRAPHIC_ORGANIZERS** - Visual organization tools
4. **SENTENCE_FRAMES** - Language structure support
5. **WORD_BANK** - Vocabulary support
6. **VISUAL_SUPPORTS** - Visual schedules/aids
7. **CALCULATOR** - Math tools
8. **REDUCED_QUESTIONS** - Fewer questions, same content
9. **AUDIO_RECORDINGS** - Recorded lectures
10. **MOVEMENT_BREAKS** - Kinesthetic breaks
11. **PREFERENTIAL_SEATING** - Strategic seating
12. **SCRIBE** - Written support

## Realistic Characteristics

- **Diverse Names**: Representing various backgrounds
- **Realistic Mastery Ranges**: Based on actual classroom distributions
- **Evidence-Based Accommodations**: IDEA-compliant modifications
- **Learning Preferences**: Mix of visual, auditory, kinesthetic, reading
- **Engagement Levels**: High, medium, low
- **Teacher Notes**: Insights into each student's strengths/challenges

## Use Cases

1. **Pipeline Testing**: Run complete lesson generation for realistic class
2. **Differentiation Demo**: Show 3-tier worksheet generation
3. **IEP Compliance**: Demonstrate FERPA-compliant modifications
4. **Cost Estimation**: Calculate per-lesson costs for 18-student class
5. **Bayesian Updates**: Test mastery tracking with realistic starting points
6. **Adaptive Planning**: Demonstrate ZPD-based personalization

## Data Schema

See `src/student_model/schemas.py` for complete Pydantic schema definitions:
- `StudentProfileCreate`
- `IEPCreate`
- `AccommodationCreate`
- `ConceptMasteryCreate`

## License

This synthetic data is for testing and demonstration purposes only.
No actual student data is included.
