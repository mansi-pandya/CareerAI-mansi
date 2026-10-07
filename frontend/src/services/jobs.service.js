import api from './api'

const JobsService = {
  // ── Search ────────────────────────────────────────────────────────────────

  searchJobs: (params = {}) => {
    const query = {}
    if (params.keywords) query.keywords = params.keywords
    if (params.jobType) query.job_type = params.jobType
    if (params.workMode) query.work_mode = params.workMode
    if (params.location) query.location = params.location
    if (params.skills?.length) query.skills = params.skills.join(',')
    if (params.salaryMin) query.salary_min = params.salaryMin
    if (params.salaryMax) query.salary_max = params.salaryMax
    if (params.company) query.company = params.company
    if (params.source) query.source = params.source
    if (params.page) query.page = params.page
    if (params.limit) query.limit = params.limit
    if (params.sortBy) query.sort_by = params.sortBy
    return api.get('/jobs/search', { params: query }).then((r) => r.data)
  },

  // ── Job Detail ────────────────────────────────────────────────────────────

  getJob: (jobId) =>
    api.get(`/jobs/${jobId}`).then((r) => r.data),

  // ── Matching ──────────────────────────────────────────────────────────────

  triggerMatch: () =>
    api.post('/jobs/match').then((r) => r.data),

  getRecommended: (limit = 10) =>
    api.get('/jobs/recommended', { params: { limit } }).then((r) => r.data),

  // ── Saved Jobs ────────────────────────────────────────────────────────────

  saveJob: (jobId) =>
    api.post(`/jobs/save/${jobId}`).then((r) => r.data),

  unsaveJob: (jobId) =>
    api.delete(`/jobs/save/${jobId}`).then((r) => r.data),

  updateSavedStatus: (jobId, status, notes = null) => {
    const params = { status }
    if (notes !== null) params.notes = notes
    return api.put(`/jobs/save/${jobId}/status`, null, { params }).then((r) => r.data)
  },

  getSavedJobs: (status = null) => {
    const params = {}
    if (status) params.status = status
    return api.get('/jobs/saved', { params }).then((r) => r.data)
  },

  // ── Market Analysis ───────────────────────────────────────────────────────

  getMarketSkills: () =>
    api.get('/jobs/market/skills').then((r) => r.data),

  getMarketTrends: () =>
    api.get('/jobs/market/trends').then((r) => r.data),

  // ── Refresh ───────────────────────────────────────────────────────────────

  refreshJobs: (keywords = 'software developer', location = 'India') =>
    api
      .post('/jobs/refresh', null, { params: { keywords, location } })
      .then((r) => r.data),
}

export default JobsService
