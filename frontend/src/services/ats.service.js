import api from './api'

const atsService = {
  // Run ATS analysis (optionally with job description)
  analyze: (resumeId, jobDescription = null) =>
    api.post(`/ats/analyze/${resumeId}`, { job_description: jobDescription }),

  // Get latest ATS result
  getResults: (resumeId) => api.get(`/ats/results/${resumeId}`),

  // Get score history (for improvement chart)
  getHistory: (resumeId) => api.get(`/ats/history/${resumeId}`),

  // Run analysis with a job description
  analyzeWithJob: (resumeId, jobDescription) =>
    api.post(`/ats/analyze-with-job/${resumeId}`, { job_description: jobDescription }),

  // Get recommendations for a specific ATS score
  getRecommendations: (atsScoreId) => api.get(`/ats/recommendations/${atsScoreId}`),
}

export default atsService
