import api from './api'

const interviewsService = {
  /**
   * Start a new interview session.
   * @param {object} params
   * @param {string} params.target_career
   * @param {string} [params.target_role]
   * @param {'hr'|'technical'|'coding'|'behavioral'|'project_based'|'mixed'} params.interview_type
   * @param {'beginner'|'intermediate'|'advanced'} params.difficulty
   * @param {string} [params.job_description]
   * @param {number} [params.job_id]
   */
  start: (params) => api.post('/interviews/start', params),

  /** Get next unanswered question */
  nextQuestion: (interviewId) => api.get(`/interviews/${interviewId}/next-question`),

  /**
   * Submit an answer for the current question.
   * @param {number} interviewId
   * @param {string} answerText
   */
  submitAnswer: (interviewId, answerText) =>
    api.post(`/interviews/${interviewId}/answer`, { answer_text: answerText }),

  /** Complete the interview and get full scores + improvements. */
  complete: (interviewId) => api.post(`/interviews/${interviewId}/complete`),

  /** Get full interview detail (questions + answers + scores). */
  get: (interviewId) => api.get(`/interviews/${interviewId}`),

  /** Get user's interview history. */
  history: () => api.get('/interviews/history'),

  /** Get improvement recommendations for a completed interview. */
  improvements: (interviewId) => api.get(`/interviews/${interviewId}/improvements`),

  /** Abandon / delete an interview. */
  delete: (interviewId) => api.delete(`/interviews/${interviewId}`),

  /** List career options available for interview setup. */
  careers: () => api.get('/interviews/careers'),
}

export default interviewsService
