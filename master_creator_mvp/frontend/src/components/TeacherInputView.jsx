import React, { useState } from 'react';
import { BookOpen, Clock, Users, FileText, Target } from 'lucide-react';
import api from '../services/api';

const TeacherInputView = ({ onPipelineStart }) => {
  const [formData, setFormData] = useState({
    grade: '9',
    subject: 'Science',
    topic: '',
    durationDays: 3,
    durationMinutes: 45,
    standards: [],
    classId: '',
  });

  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);

  const subjects = ['Science', 'Math', 'ELA', 'Social Studies'];
  const grades = ['9', '10', '11', '12'];

  const handleStandardsChange = (e) => {
    const standardsText = e.target.value;
    const standardsArray = standardsText
      .split('\n')
      .map(s => s.trim())
      .filter(s => s.length > 0);
    setFormData({ ...formData, standards: standardsArray });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Step 1: Generate Unit Plan (Engine 0)
      console.log('Generating unit plan...');
      const unitPlan = await api.generateUnitPlan({
        grade: formData.grade,
        subject: formData.subject,
        topic: formData.topic,
        durationDays: formData.durationDays,
        standards: formData.standards,
        classId: formData.classId,
      });

      console.log('Unit plan generated:', unitPlan);

      // Step 2: Generate First Lesson (Engine 1)
      console.log('Generating lesson...');
      const lesson = await api.generateLesson({
        grade: formData.grade,
        subject: formData.subject,
        topic: formData.topic,
        durationMinutes: formData.durationMinutes,
        standards: formData.standards,
        classId: formData.classId,
      });

      console.log('Lesson generated:', lesson);

      // Notify parent component to start pipeline monitoring
      if (onPipelineStart) {
        onPipelineStart({
          unitPlanId: unitPlan.unit_plan?.unit_id,
          lessonId: lesson.lesson?.lesson_id,
          jobId: lesson.pipeline_job_id || `job_${Date.now()}`,
          lesson: lesson.lesson,
          cost: lesson.cost,
        });
      }

    } catch (error) {
      console.error('Error starting pipeline:', error);
      alert(`Failed to generate lesson plan: ${error.message || 'Please try again.'}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto bg-white rounded-xl shadow-lg p-8">
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-800 mb-2">
          Master Creator v3 - 9 Engine MVP
        </h2>
        <p className="text-gray-600">
          Generate differentiated lesson materials for your ICT classroom
        </p>
      </div>

      {/* Progress Indicator */}
      <div className="mb-8 flex items-center justify-center gap-4">
        <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
          currentStep === 1 ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'
        }`}>
          <BookOpen size={20} />
          <span className="font-semibold">Unit Planning</span>
        </div>
        <div className="w-8 h-0.5 bg-gray-300" />
        <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
          currentStep === 2 ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'
        }`}>
          <FileText size={20} />
          <span className="font-semibold">Lesson Details</span>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Info Section */}
        <div className="bg-blue-50 border-l-4 border-blue-500 p-6 rounded-r-lg">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <Target size={20} className="text-blue-600" />
            Basic Information
          </h3>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Grade Level
              </label>
              <select
                value={formData.grade}
                onChange={(e) => setFormData({ ...formData, grade: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {grades.map(g => (
                  <option key={g} value={g}>{g}th Grade</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Subject
              </label>
              <select
                value={formData.subject}
                onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {subjects.map(s => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="mt-4">
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Lesson Topic
            </label>
            <input
              type="text"
              value={formData.topic}
              onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
              placeholder="e.g., Photosynthesis Process"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4 mt-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                <Clock size={16} className="inline mr-2" />
                Unit Duration (Days)
              </label>
              <input
                type="number"
                min="1"
                max="10"
                value={formData.durationDays}
                onChange={(e) => setFormData({ ...formData, durationDays: parseInt(e.target.value) })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                <Clock size={16} className="inline mr-2" />
                Lesson Duration (Minutes)
              </label>
              <input
                type="number"
                value={formData.durationMinutes}
                onChange={(e) => setFormData({ ...formData, durationMinutes: parseInt(e.target.value) })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        {/* Class Information */}
        <div className="bg-purple-50 border-l-4 border-purple-500 p-6 rounded-r-lg">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <Users size={20} className="text-purple-600" />
            Class Information
          </h3>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Class ID (Optional)
            </label>
            <input
              type="text"
              value={formData.classId}
              onChange={(e) => setFormData({ ...formData, classId: e.target.value })}
              placeholder="e.g., class_bio_101"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
            <p className="text-xs text-gray-600 mt-1">
              If provided, system will query Student Model for class-specific adaptations
            </p>
          </div>
        </div>

        {/* Standards Section */}
        <div className="bg-green-50 border-l-4 border-green-500 p-6 rounded-r-lg">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Standards Alignment (Optional)
          </h3>
          <textarea
            placeholder="e.g., NGSS-HS-LS1-5&#10;NGSS-HS-LS1-6&#10;(One standard per line)"
            value={formData.standards.join('\n')}
            onChange={handleStandardsChange}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            rows="3"
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading || !formData.topic}
          className={`w-full py-4 px-6 rounded-lg font-bold text-white text-lg transition-all
            ${loading || !formData.topic
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 hover:shadow-xl'
            }`}
        >
          {loading ? (
            <span className="flex items-center justify-center gap-3">
              <div className="w-6 h-6 border-3 border-white border-t-transparent rounded-full animate-spin" />
              Generating Lesson Blueprint...
            </span>
          ) : (
            <span>Generate Lesson (Engine 0 + Engine 1)</span>
          )}
        </button>

        {/* Engine Preview */}
        {!loading && (
          <div className="text-center text-sm text-gray-500">
            Will execute: Engine 0 (Unit Plan) → Engine 1 (Lesson Blueprint)
          </div>
        )}
      </form>
    </div>
  );
};

export default TeacherInputView;
