import axios from 'axios';

const API_BASE = '/api';
const WS_BASE = window.location.protocol === 'https:' ? 'wss://' : 'ws://';

class MasterCreatorAPI {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // WebSocket for real-time pipeline updates
    this.ws = null;
  }

  // ==================== ENGINE 0: UNIT PLAN DESIGNER ====================
  async generateUnitPlan(params) {
    const response = await this.client.post('/lessons/units', {
      unit_title: params.topic,
      grade_level: params.grade,
      subject: params.subject,
      num_lessons: params.durationDays || 3,
      standards: params.standards || [],
      class_id: params.classId,
    });
    return response.data;
  }

  // ==================== ENGINE 1: LESSON ARCHITECT ====================
  async generateLesson(params) {
    const response = await this.client.post('/lessons/lessons', {
      topic: params.topic,
      grade_level: params.grade,
      subject: params.subject,
      duration_minutes: params.durationMinutes || 45,
      standards: params.standards || [],
      class_id: params.classId,
    });
    return response.data;
  }

  async getLessonBlueprint(lessonId) {
    const response = await this.client.get(`/lessons/lessons/${lessonId}`);
    return response.data;
  }

  // ==================== ENGINE 5: DIAGNOSTIC ENGINE ====================
  async runDiagnostic(params) {
    const response = await this.client.post('/assessments/diagnostic', {
      student_ids: params.studentIds,
      concept_ids: params.conceptIds,
      lesson_id: params.lessonId,
    });
    return response.data;
  }

  async getStudentKnowledgeState(studentId) {
    const response = await this.client.get(`/students/${studentId}/mastery`);
    return response.data;
  }

  // ==================== ENGINE 2: WORKSHEET DESIGNER ====================
  async generateWorksheet(params) {
    const response = await this.client.post('/worksheets/generate', {
      lesson_id: params.lessonId,
      student_ids: params.studentIds,
      focus_objective: params.focusObjective,
    });
    return response.data;
  }

  async getWorksheetThreeTiers(worksheetId) {
    const response = await this.client.get(`/worksheets/${worksheetId}/tiers`);
    return response.data;
  }

  // ==================== ENGINE 3: IEP MODIFICATION SPECIALIST ====================
  async applyIEPModifications(params) {
    const response = await this.client.post('/worksheets/iep-modifications', {
      worksheet_id: params.worksheetId,
      student_id: params.studentId,
    });
    return response.data;
  }

  async getAppliedAccommodations(studentId, worksheetId) {
    const response = await this.client.get(
      `/students/${studentId}/accommodations`
    );
    return response.data;
  }

  // ==================== ENGINE 4: ADAPTIVE PERSONALIZATION ====================
  async generateAdaptivePathway(params) {
    const response = await this.client.post('/adaptive/generate', {
      student_id: params.studentId,
      worksheet_id: params.worksheetId,
      current_mastery: params.currentMastery,
    });
    return response.data;
  }

  async getAdaptiveBranches(studentId, worksheetId) {
    const response = await this.client.get(
      `/adaptive/student/${studentId}/branches`
    );
    return response.data;
  }

  // ==================== ASSESSMENT GRADER ====================
  async gradeWorksheet(params) {
    const response = await this.client.post('/assessments/grade', {
      worksheet_id: params.worksheetId,
      student_id: params.studentId,
      responses: params.responses,
    });
    return response.data;
  }

  async getGradingResults(gradingJobId) {
    const response = await this.client.get(`/assessments/results/${gradingJobId}`);
    return response.data;
  }

  // ==================== ENGINE 6: FEEDBACK LOOP ====================
  async processFeedback(params) {
    const response = await this.client.post('/adaptive/feedback', {
      student_id: params.studentId,
      predicted_score: params.predictedScore,
      actual_score: params.actualScore,
      question_id: params.questionId,
    });
    return response.data;
  }

  async getPredictionAccuracy(studentId) {
    const response = await this.client.get(`/adaptive/accuracy/${studentId}`);
    return response.data;
  }

  // ==================== STUDENT MODEL ====================
  async getStudentProfile(studentId) {
    const response = await this.client.get(`/students/${studentId}`);
    return response.data;
  }

  async getClassRoster(classId) {
    const response = await this.client.get(`/students/class/${classId}`);
    return response.data;
  }

  // ==================== PIPELINE MONITORING ====================
  async getPipelineStatus(jobId) {
    const response = await this.client.get(`/pipeline/status/${jobId}`);
    return response.data;
  }

  // WebSocket connection for real-time pipeline updates
  connectToPipeline(jobId, onMessage) {
    const wsUrl = `${WS_BASE}${window.location.host}/ws/pipeline/${jobId}`;
    this.ws = new WebSocket(wsUrl);

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return this.ws;
  }

  disconnectPipeline() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export default new MasterCreatorAPI();
