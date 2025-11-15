# Engine 4 Integration - Adaptive Personalization

## Overview

This document describes the integration of Engine 4 (Adaptive Personalization) with the Student Performance Dashboard, enabling real-time generation of personalized learning recommendations.

## Features Implemented

### 1. API Integration (`frontend/src/services/api.js`)

Updated Engine 4 methods to match actual backend endpoints:

```javascript
// Generate class-wide adaptive plan
async generateAdaptivePlan(params) {
  POST /api/adaptive/plan
  Body: { class_id, concept_ids }
}

// Generate personalized learning path for individual student
async generateStudentPath(studentId, conceptIds) {
  POST /api/adaptive/students/{studentId}/path
  Body: { concept_ids }
}

// Retrieve saved adaptive plan
async getAdaptivePlan(planId) {
  GET /api/adaptive/plans/{planId}
}
```

### 2. Dashboard Integration (`frontend/src/components/StudentPerformanceDashboard.jsx`)

#### New State Management

```javascript
const [adaptiveRecommendations, setAdaptiveRecommendations] = useState(null);
const [generatingRecommendations, setGeneratingRecommendations] = useState(false);
```

#### Generate Recommendations Function

```javascript
const generateAdaptiveRecommendations = async (student) => {
  // 1. Extract concept IDs from student's knowledge state
  // 2. Call Engine 4 API to generate personalized path
  // 3. Display recommendations in UI
  // 4. Handle errors gracefully
}
```

#### UI Components

**Generate Button:**
- Calls Engine 4 API when clicked
- Shows loading spinner during generation
- Disabled state while processing
- Changes text to "Regenerate" after first generation

**Recommendations Display:**
- Path ID
- Personalization level
- Detailed recommendations list
- Zone of Proximal Development (ZPD) guidance
- Styled with green border to differentiate from base recommendations

## User Flow

1. **View Student**: Teacher selects a student from the dashboard
2. **Generate Recommendations**: Click "Generate Detailed Recommendations" button
3. **API Call**: System sends student ID and concept IDs to Engine 4
4. **Processing**: Loading indicator shows while Engine 4 analyzes
5. **Display Results**: Personalized learning path appears below base recommendations
6. **Switch Students**: Recommendations clear when selecting different student
7. **Regenerate**: Can regenerate recommendations at any time

## Technical Details

### Data Flow

```
Student Dashboard
    ↓
Extract concept IDs from student.standards
    ↓
API Call: POST /api/adaptive/students/{studentId}/path
    ↓
Engine 4 (Backend)
    ├─ Query Student Model for current mastery
    ├─ Analyze learning patterns
    ├─ Generate ZPD recommendations
    └─ Create personalized learning path
    ↓
Response: { learning_path: {...} }
    ↓
Update UI with recommendations
```

### Backend Endpoint (Reference)

**POST `/api/adaptive/students/{student_id}/path`**

Request:
```json
{
  "concept_ids": ["photosynthesis_process", "cellular_respiration"]
}
```

Response:
```json
{
  "status": "success",
  "learning_path": {
    "path_id": "path_abc123",
    "student_id": "student_001",
    "personalization_level": "high",
    "recommendations": [
      "Focus on visual supports for photosynthesis",
      "Practice with scaffolded worksheets (Tier 2)"
    ],
    "zpd_recommendations": [
      "Target concepts at 60-75% mastery",
      "Provide moderate scaffolding"
    ]
  }
}
```

## Error Handling

- Network errors: Display user-friendly error message
- API failures: Console logging for debugging
- Empty concept IDs: Gracefully handle with empty array
- Loading states: Prevent duplicate requests

## UI/UX Enhancements

1. **Visual Feedback**:
   - Spinner animation during generation
   - Green border for Engine 4 recommendations
   - Lightbulb icon for visual distinction

2. **State Management**:
   - Clear recommendations on student change
   - Disable button during processing
   - Toggle button text (Generate/Regenerate)

3. **Accessibility**:
   - Disabled state clearly indicated
   - Loading state announced to screen readers
   - Semantic HTML structure

## Testing

### Manual Testing

1. Start backend: `python run_server.py`
2. Start frontend: `npm run dev`
3. Navigate to Student Dashboard
4. Select a student
5. Click "Generate Detailed Recommendations"
6. Verify:
   - Loading spinner appears
   - API call succeeds
   - Recommendations display
   - Can regenerate
   - Recommendations clear on student change

### API Testing

```bash
# Test student path generation
curl -X POST http://localhost:8080/api/adaptive/students/student_001/path \
  -H "Content-Type: application/json" \
  -d '{"concept_ids": ["photosynthesis_process"]}'

# Verify response includes learning_path object
```

## Future Enhancements

1. **Save Recommendations**: Store generated paths in database for historical tracking
2. **Implementation Tracking**: Track which recommendations were implemented
3. **Effectiveness Metrics**: Measure impact of recommendations on student performance
4. **Batch Generation**: Generate recommendations for all students at once
5. **Export to PDF**: Allow teachers to export recommendations
6. **Integration with Lesson Plans**: Link recommendations directly to lesson generation

## Related Files

- `frontend/src/components/StudentPerformanceDashboard.jsx` - UI component
- `frontend/src/services/api.js` - API client
- `src/api/routes/adaptive.py` - Backend endpoints
- `src/engines/engine_4_adaptive.py` - Engine implementation
- `src/content_storage/interface.py` - Storage for generated plans

## Dependencies

- **Frontend**: React 18, Lucide icons
- **Backend**: FastAPI, Engine 4 (AdaptiveEngine)
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **API**: RESTful HTTP

## Notes

- Recommendations are session-based (not persisted by default)
- Concept IDs are extracted from student's standards data
- Empty concept arrays are handled gracefully
- Loading states prevent duplicate API calls
- Error messages are user-friendly and actionable
