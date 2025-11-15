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

    // WebSockets for real-time updates
    this.pipelineWs = null;
    this.dashboardWs = null;
    this.studentWs = null;
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
  async generateAdaptivePlan(params) {
    const response = await this.client.post('/adaptive/plan', {
      class_id: params.classId,
      concept_ids: params.conceptIds,
    });
    return response.data;
  }

  async generateStudentPath(studentId, conceptIds) {
    const response = await this.client.post(`/adaptive/students/${studentId}/path`, {
      concept_ids: conceptIds,
    });
    return response.data;
  }

  async getAdaptivePlan(planId) {
    const response = await this.client.get(`/adaptive/plans/${planId}`);
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

  // ==================== WEBSOCKET CONNECTIONS ====================

  // WebSocket connection for real-time pipeline updates
  connectToPipeline(jobId, onMessage) {
    const wsUrl = `${WS_BASE}${window.location.host}/ws/pipeline/${jobId}`;
    this.pipelineWs = new WebSocket(wsUrl);

    this.pipelineWs.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    this.pipelineWs.onerror = (error) => {
      console.error('Pipeline WebSocket error:', error);
    };

    this.pipelineWs.onclose = () => {
      console.log('Pipeline WebSocket disconnected');
    };

    return this.pipelineWs;
  }

  disconnectPipeline() {
    if (this.pipelineWs) {
      this.pipelineWs.close();
      this.pipelineWs = null;
    }
  }

  // WebSocket connection for real-time dashboard updates
  connectToDashboard(classId, onMessage, onError = null) {
    // Close existing connection if any
    this.disconnectDashboard();

    const wsUrl = `${WS_BASE}${window.location.host}/ws/dashboard/${classId}`;
    this.dashboardWs = new WebSocket(wsUrl);

    this.dashboardWs.onopen = () => {
      console.log(`Dashboard WebSocket connected to class ${classId}`);
    };

    this.dashboardWs.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    this.dashboardWs.onerror = (error) => {
      console.error('Dashboard WebSocket error:', error);
      if (onError) onError(error);
    };

    this.dashboardWs.onclose = () => {
      console.log('Dashboard WebSocket disconnected');
    };

    // Set up heartbeat to keep connection alive
    const heartbeatInterval = setInterval(() => {
      if (this.dashboardWs && this.dashboardWs.readyState === WebSocket.OPEN) {
        this.dashboardWs.send('ping');
      } else {
        clearInterval(heartbeatInterval);
      }
    }, 30000); // Ping every 30 seconds

    return this.dashboardWs;
  }

  disconnectDashboard() {
    if (this.dashboardWs) {
      this.dashboardWs.close();
      this.dashboardWs = null;
    }
  }

  // WebSocket connection for individual student updates
  connectToStudent(studentId, onMessage, onError = null) {
    // Close existing connection if any
    this.disconnectStudent();

    const wsUrl = `${WS_BASE}${window.location.host}/ws/student/${studentId}`;
    this.studentWs = new WebSocket(wsUrl);

    this.studentWs.onopen = () => {
      console.log(`Student WebSocket connected to student ${studentId}`);
    };

    this.studentWs.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    this.studentWs.onerror = (error) => {
      console.error('Student WebSocket error:', error);
      if (onError) onError(error);
    };

    this.studentWs.onclose = () => {
      console.log('Student WebSocket disconnected');
    };

    // Set up heartbeat to keep connection alive
    const heartbeatInterval = setInterval(() => {
      if (this.studentWs && this.studentWs.readyState === WebSocket.OPEN) {
        this.studentWs.send('ping');
      } else {
        clearInterval(heartbeatInterval);
      }
    }, 30000); // Ping every 30 seconds

    return this.studentWs;
  }

  disconnectStudent() {
    if (this.studentWs) {
      this.studentWs.close();
      this.studentWs = null;
    }
  }

  // Disconnect all WebSocket connections
  disconnectAll() {
    this.disconnectPipeline();
    this.disconnectDashboard();
    this.disconnectStudent();
  }
}

export default new MasterCreatorAPI();
