import api from './api'

const resumeService = {
  // Upload a PDF/DOCX file
  upload: (file, title = 'My Resume', onProgress) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('title', title)
    return api.post('/resume/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: onProgress
        ? (e) => onProgress(Math.round((e.loaded * 100) / (e.total || 1)))
        : undefined,
    })
  },

  // List all resumes
  list: () => api.get('/resume/list'),

  // Get resume detail (with sections and versions)
  get: (resumeId) => api.get(`/resume/${resumeId}`),

  // Update a resume (title, is_active, parsed_data)
  update: (resumeId, data) => api.put(`/resume/${resumeId}`, data),

  // Delete a resume
  delete: (resumeId) => api.delete(`/resume/${resumeId}`),

  // Create resume from builder form
  createFromBuilder: (formData) => api.post('/resume/builder', formData),

  // List versions of a resume
  listVersions: (resumeId) => api.get(`/resume/${resumeId}/versions`),

  // AI improve a section
  aiImprove: (resumeId, section, field, currentText) =>
    api.post(`/resume/${resumeId}/ai-improve`, {
      section,
      field,
      current_text: currentText,
    }),

  // Set a resume as active (deactivates others)
  setActive: (resumeId) =>
    api.put(`/resume/${resumeId}`, { is_active: true }),
}

export default resumeService
