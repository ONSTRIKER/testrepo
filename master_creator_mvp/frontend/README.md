# Master Creator v3 MVP - Frontend

React + Vite frontend for the Master Creator adaptive learning system.

## Structure

```
frontend/
├── src/
│   ├── components/        # React components (to be added)
│   │   ├── TeacherInputView.jsx
│   │   ├── PipelineMonitor.jsx
│   │   ├── StudentDashboard.jsx
│   │   ├── WorksheetPreview.jsx
│   │   ├── DiagnosticResults.jsx
│   │   └── FeedbackAnalytics.jsx
│   ├── services/
│   │   └── api.js         # API client
│   ├── App.jsx            # Main app component (to be added)
│   ├── main.jsx           # Entry point
│   └── index.css          # Global styles
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will run on http://localhost:3000 and proxy API requests to the FastAPI backend on port 8080.

## Components (Template Provided)

All component files have been provided as templates. To implement:

1. Create each component file in `src/components/`
2. Import and use them in `src/App.jsx`
3. Connect to the API service layer

## API Integration

The `services/api.js` file provides methods for all 9 engines:

- Engine 0: Unit Plan Designer
- Engine 1: Lesson Architect
- Engine 2: Worksheet Designer
- Engine 3: IEP Modifications
- Engine 4: Adaptive Personalization
- Engine 5: Diagnostic Engine
- Engine 6: Feedback Loop
- Grader: Assessment Grader
- Student Model: Student data access

## Development

The frontend uses:
- **React 18** for UI
- **Vite** for fast development
- **Tailwind CSS** for styling
- **Axios** for API calls
- **Recharts** for data visualization
- **Lucide React** for icons

To add component files, create them in `src/components/` following the templates provided in the project documentation.
