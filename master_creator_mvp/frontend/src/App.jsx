import React, { useState } from 'react';
import TeacherInputView from './components/TeacherInputView';
import PipelineMonitor from './components/PipelineMonitor';
import StudentPerformanceDashboard from './components/StudentPerformanceDashboard';

const App = () => {
  const [view, setView] = useState('input'); // input, pipeline, dashboard
  const [pipelineData, setPipelineData] = useState(null);

  const handlePipelineStart = (data) => {
    setPipelineData(data);
    setView('pipeline');
  };

  const handlePipelineComplete = (data) => {
    console.log('Pipeline complete:', data);
    // Optionally switch to dashboard view after completion
    setTimeout(() => {
      setView('dashboard');
    }, 3000);
  };

  const TAB_CONFIG = [
    { id: 'input', name: 'Generate Lesson', icon: '📝', enabled: true },
    { id: 'pipeline', name: 'Pipeline Monitor', icon: '⚙️', enabled: !!pipelineData },
    { id: 'dashboard', name: 'Student Dashboard', icon: '👥', enabled: true },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-md border-b-2 border-indigo-200">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                Master Creator v3 MVP
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                9-Engine Adaptive Learning System for Special Education ICT Classrooms
              </p>
            </div>

            <div className="flex items-center gap-4">
              <div className="text-right text-sm text-gray-600">
                <div><strong>Status:</strong> MVP Active</div>
                <div className="text-xs">Powered by Claude Sonnet 4</div>
              </div>

              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white font-bold text-xl">
                MC
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white border-b-2 border-gray-200 sticky top-0 z-40 shadow-sm">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex gap-2 overflow-x-auto py-3">
            {TAB_CONFIG.map(tab => (
              <button
                key={tab.id}
                onClick={() => tab.enabled && setView(tab.id)}
                disabled={!tab.enabled}
                className={`
                  px-4 py-2 rounded-lg font-semibold text-sm whitespace-nowrap transition-all
                  flex items-center gap-2
                  ${view === tab.id
                    ? 'bg-blue-600 text-white shadow-lg'
                    : tab.enabled
                    ? 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    : 'bg-gray-50 text-gray-400 cursor-not-allowed'
                  }
                `}
              >
                <span className="text-lg">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="max-w-[1920px] mx-auto p-6">
        {view === 'input' && (
          <div className="fade-in">
            <TeacherInputView onPipelineStart={handlePipelineStart} />
          </div>
        )}

        {view === 'pipeline' && pipelineData && (
          <div className="fade-in">
            <PipelineMonitor
              jobId={pipelineData.jobId}
              lessonData={pipelineData}
              onComplete={handlePipelineComplete}
            />
          </div>
        )}

        {view === 'dashboard' && (
          <div className="fade-in">
            <StudentPerformanceDashboard classId="class_001" />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t-2 border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="grid grid-cols-3 gap-6 text-sm text-gray-600">
            <div>
              <h4 className="font-semibold text-gray-800 mb-2">9-Engine MVP Pipeline</h4>
              <div className="space-y-1 text-xs">
                <div>✅ Engine 0: Unit Plan Designer</div>
                <div>✅ Engine 1: Lesson Architect</div>
                <div>🔄 Engine 5: Diagnostic (BKT)</div>
                <div>🔄 Engine 2: Worksheet Designer</div>
                <div>🔄 Engine 3: IEP Modifications</div>
                <div>🔄 Engine 4: Adaptive Personalization</div>
                <div>🔄 Assessment Grader</div>
                <div>🔄 Engine 6: Feedback Loop</div>
                <div className="font-semibold text-slate-600">✅ Student Model Hub (PostgreSQL + Chroma)</div>
              </div>
            </div>

            <div>
              <h4 className="font-semibold text-gray-800 mb-2">Technology Stack</h4>
              <div className="space-y-1 text-xs">
                <div>Frontend: React + Vite + Tailwind CSS</div>
                <div>Backend: FastAPI + Python</div>
                <div>LLM: Claude Sonnet 4 (Anthropic)</div>
                <div>Database: SQLite (MVP) → PostgreSQL</div>
                <div>Charts: Recharts</div>
              </div>
            </div>

            <div>
              <h4 className="font-semibold text-gray-800 mb-2">Compliance & Standards</h4>
              <div className="space-y-1 text-xs">
                <div>✓ IDEA 2004 compliant</div>
                <div>✓ Section 504 accommodations</div>
                <div>✓ FERPA data privacy</div>
                <div>✓ UDL framework integrated</div>
                <div>✓ Evidence-based practices</div>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-6 border-t border-gray-200 text-center text-xs text-gray-500">
            Master Creator v3 MVP • Integrated with Student Model Interface • Real-time adaptive learning analytics
          </div>
        </div>
      </footer>

      <style>{`
        .fade-in {
          animation: fadeIn 0.5s ease-in;
        }

        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
};

export default App;
