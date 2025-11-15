import React, { useState, useEffect } from 'react';
import { CheckCircle, Clock, AlertCircle, Loader, XCircle } from 'lucide-react';

const PipelineMonitor = ({ jobId, lessonData, onComplete }) => {
  const [pipelineState, setPipelineState] = useState({
    status: 'running',
    currentStage: 'engine_1',
    completedStages: ['engine_0', 'engine_1'],
    stages: {},
    startTime: Date.now(),
  });

  const MVP_STAGES = [
    {
      id: 'engine_0',
      name: 'Unit Plan Designer',
      icon: '📚',
      color: 'emerald',
      description: 'UbD framework + multi-day coherence'
    },
    {
      id: 'engine_1',
      name: 'Lesson Architect',
      icon: '📐',
      color: 'blue',
      description: '10-part lesson blueprint + standards alignment'
    },
    {
      id: 'engine_5',
      name: 'Diagnostic Engine',
      icon: '🔍',
      color: 'red',
      description: 'Bayesian Knowledge Tracing (simulated for MVP)'
    },
    {
      id: 'engine_2',
      name: 'Worksheet Designer',
      icon: '📝',
      color: 'green',
      description: '3-tier differentiation (simulated for MVP)'
    },
    {
      id: 'engine_3',
      name: 'IEP Modification Specialist',
      icon: '🔧',
      color: 'purple',
      description: 'Legal compliance + accommodations (simulated)'
    },
    {
      id: 'engine_4',
      name: 'Adaptive Personalization',
      icon: '🎯',
      color: 'amber',
      description: 'Dynamic branching logic (simulated)'
    },
    {
      id: 'grader',
      name: 'Assessment Grader',
      icon: '✅',
      color: 'teal',
      description: 'MC + constructed response (simulated)'
    },
    {
      id: 'engine_6',
      name: 'Feedback Loop',
      icon: '🔄',
      color: 'cyan',
      description: 'Prediction accuracy + Bayesian updates (simulated)'
    }
  ];

  useEffect(() => {
    // Simulate pipeline progression for MVP
    // In production, this would use WebSocket connection
    let currentStageIndex = 2; // Start after Engine 0 and 1 (already complete)

    const progressInterval = setInterval(() => {
      if (currentStageIndex < MVP_STAGES.length) {
        const stage = MVP_STAGES[currentStageIndex];

        setPipelineState(prevState => ({
          ...prevState,
          currentStage: stage.id,
          completedStages: [...new Set([...prevState.completedStages, stage.id])],
          stages: {
            ...prevState.stages,
            [stage.id]: {
              status: 'complete',
              startTime: Date.now() - (2000 * currentStageIndex),
              endTime: Date.now(),
              duration: 1500 + Math.random() * 1000,
            }
          }
        }));

        currentStageIndex++;
      } else {
        // Pipeline complete
        setPipelineState(prevState => ({
          ...prevState,
          status: 'complete',
        }));

        clearInterval(progressInterval);

        if (onComplete) {
          onComplete({
            status: 'complete',
            lessonId: lessonData?.lesson_id,
            cost: lessonData?.cost || { total_cost: 0.0629 },
          });
        }
      }
    }, 2000); // Simulate 2 seconds per stage

    return () => clearInterval(progressInterval);
  }, [jobId, lessonData, onComplete]);

  const getStageStatus = (stageId) => {
    if (pipelineState.completedStages.includes(stageId)) {
      return 'complete';
    } else if (pipelineState.currentStage === stageId) {
      return 'processing';
    } else {
      return 'queued';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'complete': return <CheckCircle className="text-green-600" size={20} />;
      case 'processing': return <Loader className="text-blue-600 animate-spin" size={20} />;
      case 'error': return <XCircle className="text-red-600" size={20} />;
      default: return <Clock className="text-gray-400" size={20} />;
    }
  };

  const formatDuration = (ms) => {
    if (!ms) return '--';
    return `${(ms / 1000).toFixed(1)}s`;
  };

  const elapsedTime = () => {
    const elapsed = Date.now() - pipelineState.startTime;
    return Math.floor(elapsed / 1000);
  };

  return (
    <div className="max-w-6xl mx-auto bg-white rounded-xl shadow-lg p-8">
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">
          Pipeline Execution Monitor
        </h2>
        <p className="text-gray-600">
          Real-time status of 9-engine lesson generation pipeline
        </p>
        <p className="text-sm text-gray-500 mt-1">
          Job ID: {jobId} | Elapsed: {elapsedTime()}s
        </p>
      </div>

      {/* Overall Progress Bar */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-semibold text-gray-700">Overall Progress</span>
          <span className="text-sm font-semibold text-blue-600">
            {pipelineState.completedStages.length} / {MVP_STAGES.length} Engines Complete
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className="bg-gradient-to-r from-blue-500 to-indigo-600 h-3 rounded-full transition-all duration-500"
            style={{ width: `${(pipelineState.completedStages.length / MVP_STAGES.length) * 100}%` }}
          />
        </div>
      </div>

      {/* Pipeline Flow Visualization */}
      <div className="space-y-3">
        {MVP_STAGES.map((stage, index) => {
          const status = getStageStatus(stage.id);
          const stageData = pipelineState.stages[stage.id];

          return (
            <div key={stage.id}>
              <div className={`
                border-l-4 rounded-lg p-4 transition-all duration-300
                ${status === 'complete' ? `bg-${stage.color}-50 border-${stage.color}-500` :
                  status === 'processing' ? `bg-blue-50 border-blue-500 shadow-lg` :
                  'bg-gray-50 border-gray-300'}
              `}>
                <div className="flex items-center justify-between">
                  {/* Left: Engine Info */}
                  <div className="flex items-center gap-4 flex-1">
                    <span className="text-3xl">{stage.icon}</span>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-bold text-gray-800">{stage.name}</h3>
                        <span className={`
                          text-xs px-2 py-1 rounded-full font-semibold
                          ${status === 'complete' ? `bg-${stage.color}-200 text-${stage.color}-800` :
                            status === 'processing' ? 'bg-blue-200 text-blue-800' :
                            'bg-gray-200 text-gray-600'}
                        `}>
                          {stage.id.replace('engine_', 'Engine ').replace('grader', 'Grader')}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{stage.description}</p>

                      {/* Real-time metadata display */}
                      {status === 'processing' && (
                        <div className="mt-2 text-xs text-blue-600 font-mono">
                          Processing...
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Right: Status & Duration */}
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <div className="text-sm font-semibold text-gray-700">
                        {formatDuration(stageData?.duration)}
                      </div>
                      {stageData?.startTime && (
                        <div className="text-xs text-gray-500">
                          {new Date(stageData.startTime).toLocaleTimeString()}
                        </div>
                      )}
                    </div>
                    {getStatusIcon(status)}
                  </div>
                </div>

                {/* Processing indicator */}
                {status === 'processing' && (
                  <div className="mt-3">
                    <div className="w-full bg-blue-200 rounded-full h-1.5">
                      <div className="bg-blue-600 h-1.5 rounded-full animate-pulse" style={{ width: '60%' }} />
                    </div>
                  </div>
                )}
              </div>

              {/* Arrow between stages */}
              {index < MVP_STAGES.length - 1 && (
                <div className="flex justify-center my-2">
                  <div className={`
                    text-2xl transition-opacity duration-300
                    ${pipelineState.completedStages.includes(stage.id) ? 'opacity-100' : 'opacity-30'}
                  `}>
                    ↓
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Student Model Hub Indicator */}
      <div className="mt-6 p-4 bg-slate-100 border-2 border-slate-400 rounded-lg">
        <div className="flex items-center gap-3">
          <span className="text-2xl">🗄️</span>
          <div className="flex-1">
            <h4 className="font-bold text-gray-800">Student Model Hub</h4>
            <p className="text-sm text-gray-600">
              PostgreSQL + Chroma vector DB • All engines query through StudentModelInterface
            </p>
          </div>
          <div className="text-xs text-slate-600 font-mono">
            {pipelineState.completedStages.length > 0 ? 'Active' : 'Standby'}
          </div>
        </div>
      </div>

      {/* Completion Message */}
      {pipelineState.status === 'complete' && (
        <div className="mt-6 p-6 bg-green-50 border-2 border-green-500 rounded-lg">
          <div className="flex items-center gap-3">
            <CheckCircle className="text-green-600" size={32} />
            <div>
              <h3 className="text-xl font-bold text-green-800">
                Pipeline Complete! 🎉
              </h3>
              <p className="text-green-700">
                Lesson blueprint generated successfully. Cost: ${lessonData?.cost?.total_cost?.toFixed(4) || '0.0629'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Error State */}
      {pipelineState.status === 'error' && (
        <div className="mt-6 p-6 bg-red-50 border-2 border-red-500 rounded-lg">
          <div className="flex items-center gap-3">
            <AlertCircle className="text-red-600" size={32} />
            <div>
              <h3 className="text-xl font-bold text-red-800">
                Pipeline Error
              </h3>
              <p className="text-red-700">
                An error occurred during execution. Check logs for details.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Cost Summary */}
      {lessonData?.cost && (
        <div className="mt-6 p-4 bg-blue-50 border border-blue-300 rounded-lg">
          <h4 className="font-semibold text-blue-900 mb-2">Cost Summary</h4>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <p className="text-blue-700">Input Tokens</p>
              <p className="font-bold text-blue-900">{lessonData.cost.input_tokens || 0}</p>
            </div>
            <div>
              <p className="text-blue-700">Output Tokens</p>
              <p className="font-bold text-blue-900">{lessonData.cost.output_tokens || 0}</p>
            </div>
            <div>
              <p className="text-blue-700">Total Cost</p>
              <p className="font-bold text-blue-900">${lessonData.cost.total_cost?.toFixed(4) || '0.0000'}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PipelineMonitor;
