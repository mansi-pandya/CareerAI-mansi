import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import interviewsService from '../../services/interviews.service'

const INTERVIEW_TYPES = [
  {
    value: 'mixed',
    label: 'Mixed',
    icon: '🎯',
    description: 'Balanced blend of technical, HR, behavioral, and project-based questions.',
  },
  {
    value: 'technical',
    label: 'Technical',
    icon: '⚙️',
    description: 'Deep dive into technical skills, concepts, and problem-solving.',
  },
  {
    value: 'hr',
    label: 'HR',
    icon: '🤝',
    description: 'Human resources questions about motivation, fit, and career goals.',
  },
  {
    value: 'behavioral',
    label: 'Behavioral',
    icon: '🧠',
    description: 'Situation-based questions using the STAR framework.',
  },
  {
    value: 'coding',
    label: 'Coding',
    icon: '💻',
    description: 'Algorithmic and coding problem-solving questions.',
  },
  {
    value: 'project_based',
    label: 'Project-Based',
    icon: '🚀',
    description: 'Questions focused on your personal projects and engineering decisions.',
  },
]

const DIFFICULTIES = [
  {
    value: 'beginner',
    label: 'Beginner',
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/10 border-emerald-500/30',
    activeBg: 'bg-emerald-500/20 border-emerald-500',
    description: 'Foundational concepts and basic questions.',
  },
  {
    value: 'intermediate',
    label: 'Intermediate',
    color: 'text-blue-400',
    bg: 'bg-blue-500/10 border-blue-500/30',
    activeBg: 'bg-blue-500/20 border-blue-500',
    description: 'Standard industry-level questions.',
  },
  {
    value: 'advanced',
    label: 'Advanced',
    color: 'text-purple-400',
    bg: 'bg-purple-500/10 border-purple-500/30',
    activeBg: 'bg-purple-500/20 border-purple-500',
    description: 'Senior-level and in-depth questions.',
  },
]

const TIPS = [
  { icon: '🎙️', text: 'Speak or type naturally — there is no single right answer.' },
  { icon: '📐', text: 'Use the STAR method for behavioral questions: Situation, Task, Action, Result.' },
  { icon: '🔍', text: 'For technical questions, explain your reasoning, not just the answer.' },
  { icon: '⏱️', text: 'Take your time — quality of thinking matters more than speed.' },
  { icon: '💡', text: 'Reference your own projects and experience for project-based questions.' },
]

export default function InterviewSetup() {
  const navigate = useNavigate()
  const [careers, setCareers] = useState([])
  const [loading, setLoading] = useState(false)
  const [loadingCareers, setLoadingCareers] = useState(true)

  const [form, setForm] = useState({
    target_career: '',
    target_role: '',
    interview_type: 'mixed',
    difficulty: 'intermediate',
    job_description: '',
  })

  useEffect(() => {
    interviewsService
      .careers()
      .then((res) => setCareers(res.data || []))
      .catch(() => setCareers([]))
      .finally(() => setLoadingCareers(false))
  }, [])

  const handleStart = async () => {
    if (!form.target_career) {
      toast.error('Please select a target career.')
      return
    }
    setLoading(true)
    try {
      const payload = {
        target_career: form.target_career,
        interview_type: form.interview_type,
        difficulty: form.difficulty,
      }
      if (form.target_role.trim()) payload.target_role = form.target_role.trim()
      if (form.job_description.trim()) payload.job_description = form.job_description.trim()

      const res = await interviewsService.start(payload)
      const interview = res.data
      navigate(`/interview/${interview.id}`, { state: { interview } })
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Failed to start interview.'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <span className="text-3xl">🎤</span> AI Interview Practice
        </h1>
        <p className="text-gray-400 mt-1 text-sm">
          Personalized interview questions based on your profile, skills, and projects.
        </p>
      </div>

      {/* Career Selection */}
      <section className="bg-gray-900 border border-white/10 rounded-xl p-6 space-y-4">
        <h2 className="text-base font-semibold text-white">Target Career</h2>
        <div>
          <label className="block text-xs text-gray-400 mb-1">Career Path *</label>
          {loadingCareers ? (
            <div className="h-10 bg-gray-800 rounded-lg animate-pulse" />
          ) : (
            <select
              value={form.target_career}
              onChange={(e) => setForm({ ...form, target_career: e.target.value })}
              className="w-full bg-gray-800 border border-white/10 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
            >
              <option value="">Select a career...</option>
              {careers.map((c) => (
                <option key={c.slug} value={c.name}>
                  {c.name}
                </option>
              ))}
            </select>
          )}
        </div>
        <div>
          <label className="block text-xs text-gray-400 mb-1">Specific Role (optional)</label>
          <input
            type="text"
            value={form.target_role}
            onChange={(e) => setForm({ ...form, target_role: e.target.value })}
            placeholder="e.g. Senior Backend Engineer, Data Science Intern..."
            className="w-full bg-gray-800 border border-white/10 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
          />
        </div>
      </section>

      {/* Interview Type */}
      <section className="bg-gray-900 border border-white/10 rounded-xl p-6 space-y-4">
        <h2 className="text-base font-semibold text-white">Interview Type</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {INTERVIEW_TYPES.map((type) => {
            const active = form.interview_type === type.value
            return (
              <button
                key={type.value}
                onClick={() => setForm({ ...form, interview_type: type.value })}
                className={`text-left p-3 rounded-xl border transition-all ${
                  active
                    ? 'bg-blue-500/20 border-blue-500 ring-1 ring-blue-500/40'
                    : 'bg-gray-800 border-white/10 hover:border-white/30'
                }`}
              >
                <div className="text-xl mb-1">{type.icon}</div>
                <div className="text-sm font-medium text-white">{type.label}</div>
                <div className="text-xs text-gray-400 mt-0.5 leading-snug">{type.description}</div>
              </button>
            )
          })}
        </div>
      </section>

      {/* Difficulty */}
      <section className="bg-gray-900 border border-white/10 rounded-xl p-6 space-y-4">
        <h2 className="text-base font-semibold text-white">Difficulty</h2>
        <div className="flex gap-3 flex-wrap">
          {DIFFICULTIES.map((d) => {
            const active = form.difficulty === d.value
            return (
              <button
                key={d.value}
                onClick={() => setForm({ ...form, difficulty: d.value })}
                className={`flex-1 min-w-[120px] p-4 rounded-xl border transition-all ${
                  active ? d.activeBg : d.bg
                }`}
              >
                <div className={`text-sm font-semibold ${d.color}`}>{d.label}</div>
                <div className="text-xs text-gray-400 mt-1">{d.description}</div>
              </button>
            )
          })}
        </div>
      </section>

      {/* Job Description */}
      <section className="bg-gray-900 border border-white/10 rounded-xl p-6 space-y-4">
        <div>
          <h2 className="text-base font-semibold text-white">
            Job Description{' '}
            <span className="text-xs font-normal text-gray-500">(optional)</span>
          </h2>
          <p className="text-xs text-gray-500 mt-0.5">
            Paste a job posting to tailor questions to that specific role.
          </p>
        </div>
        <textarea
          value={form.job_description}
          onChange={(e) => setForm({ ...form, job_description: e.target.value })}
          rows={4}
          placeholder="Paste job description here..."
          className="w-full bg-gray-800 border border-white/10 text-white rounded-lg px-3 py-2 text-sm resize-none focus:outline-none focus:border-blue-500"
        />
      </section>

      {/* Tips */}
      <section className="bg-blue-500/5 border border-blue-500/20 rounded-xl p-5">
        <h3 className="text-sm font-semibold text-blue-300 mb-3">
          💡 How to get the most from your AI interview
        </h3>
        <ul className="space-y-2">
          {TIPS.map((tip, i) => (
            <li key={i} className="flex items-start gap-2 text-xs text-gray-300">
              <span className="text-sm">{tip.icon}</span>
              <span>{tip.text}</span>
            </li>
          ))}
        </ul>
      </section>

      {/* Start button */}
      <button
        onClick={handleStart}
        disabled={loading || !form.target_career}
        className="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-sm transition-all"
      >
        {loading ? (
          <span className="flex items-center justify-center gap-2">
            <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            Generating questions…
          </span>
        ) : (
          'Start Interview →'
        )}
      </button>
    </div>
  )
}
