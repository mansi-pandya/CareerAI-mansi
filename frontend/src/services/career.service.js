import api from './api'

const CareerService = {
  // ── Recommendations ──────────────────────────────────────────────────────

  getRecommendations: () =>
    api.get('/career/recommendations').then((r) => r.data),

  refreshRecommendations: () =>
    api.post('/career/recommendations/refresh').then((r) => r.data),

  // ── Careers ──────────────────────────────────────────────────────────────

  getCareers: () =>
    api.get('/career/careers').then((r) => r.data),

  getCareer: (slug) =>
    api.get(`/career/careers/${slug}`).then((r) => r.data),

  // ── Skill Gap ─────────────────────────────────────────────────────────────

  getSkillGap: (careerSlug) =>
    api.get(`/career/skill-gap/${careerSlug}`).then((r) => r.data),

  // ── Learning Resources ────────────────────────────────────────────────────

  getLearningResources: () =>
    api.get('/career/learning-resources').then((r) => r.data),

  getResourcesForSkill: (skill, difficulty) =>
    api
      .get(`/career/learning-resources/${encodeURIComponent(skill)}`, {
        params: difficulty ? { difficulty } : {},
      })
      .then((r) => r.data),

  // ── Learning Progress ─────────────────────────────────────────────────────

  updateProgress: (skillName, proficiencyLevel, notes = '') =>
    api
      .post('/career/learning-progress', {
        skill_name: skillName,
        proficiency_level: proficiencyLevel,
        notes,
      })
      .then((r) => r.data),

  getProgress: () =>
    api.get('/career/learning-progress').then((r) => r.data),

  // ── Roadmap ───────────────────────────────────────────────────────────────

  getRoadmap: (careerSlug) =>
    api.get(`/career/roadmap/${careerSlug}`).then((r) => r.data),

  generateRoadmap: (careerSlug) =>
    api.post(`/career/roadmap/${careerSlug}/generate`).then((r) => r.data),

  // ── What-If Simulation ────────────────────────────────────────────────────

  whatIf: (careerSlug, skills) =>
    api
      .get('/career/what-if', {
        params: {
          career_slug: careerSlug,
          skills: Array.isArray(skills) ? skills.join(',') : skills,
        },
      })
      .then((r) => r.data),
}

export default CareerService
