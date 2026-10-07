import api from './api'

const opportunitiesService = {
  /**
   * Check an opportunity.
   * @param {object} params
   * @param {'text'|'url'|'image'|'screenshot'|'pdf'} params.inputType
   * @param {string} [params.text]
   * @param {string} [params.url]
   * @param {File}   [params.file]
   * @param {function} [params.onProgress]  - (percent: number) => void
   */
  check: ({ inputType, text, url, file, onProgress }) => {
    const formData = new FormData()
    formData.append('input_type', inputType)
    if (text) formData.append('text', text)
    if (url) formData.append('url', url)
    if (file) formData.append('file', file)

    return api.post('/opportunities/check', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: onProgress
        ? (e) => onProgress(Math.round((e.loaded * 100) / (e.total || 1)))
        : undefined,
    })
  },

  /** List all past opportunity checks for the current user */
  history: () => api.get('/opportunities/history'),

  /** Get a specific opportunity check by ID */
  get: (checkId) => api.get(`/opportunities/${checkId}`),

  /** Delete an opportunity check */
  delete: (checkId) => api.delete(`/opportunities/${checkId}`),
}

export default opportunitiesService
