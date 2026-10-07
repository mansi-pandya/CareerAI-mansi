import { useState, useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts'
import resumeService from '../../services/resume.service'
import atsService from '../../services/ats.service'
import ScoreCircle from '../../components/ui/ScoreCircle'
import ProgressBar from '../../components/ui/ProgressBar'
import ATSRecommendationCard from '../../components/resume/ATSRecommendationCard'

const SUB_SCORES = [
  { key: 'structure_score', label: 'Structure', color: 'blue' },
  { key: 'formatting_score', label: 'Formatting', color: 'indigo' },
  { key: 'keyword_score', label: 'Keywords', color: 'purple' },
  { key: 'skills_score', label: 'Skills', color: 'teal' },
  { key: 'projects_score', label: 'Projects', color: 'green' },
  { key: 'experience_score', label: 'Experience', color: 'blue' },
  { key: 'education_score', label: 'Education', color: 'orange' },
  { key: 'contact_score', label: 'Contact', color: 'yellow' },
  { key: 'job_alignment_score', label: 'Job Alignment', color: 'indigo' },
]

function getScoreColor(score) {
  if (score >= 80) return 'text-emerald-400'
  if (score >= 60) return 'text-blue-400'
  if (score >= 40) return 'text-amber-400'
  return 'text-red-400'
}

function getScoreLabel(score) {
  if (score >= 80) return 'Excellent'
  if (score >= 65) return 'Good'
  if (score >= 45) return 'Needs Work'
  return 'Poor'
}

function AnalyzingState() {
  const steps = ['Parsing resume data', 'Analyzing structure', 'Checking keywords', 'Scoring dimensions', 'Generating recommendations']
  const [step, setStep] = useState(0)

  useEffect(() => {
    const t = setInterval(() => setStep((s) => Math.min(s + 1, steps.length - 1)), 600)
    return () => clearInterval(t)
  }, [])

  return (
    <div className="flex flex-col items-center justify-center py-16">
      <div className="w-14 h-14 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mb-6" />
      <p className="text-white font-medium mb-4">Analyzing your resume…</p>
      <div className="space-y-2 w-64">
        {steps.map((s, i) => (
          <div key={i} className={`flex items-center gap-2.5 text-sm transition-all ${i <= step ? 'text-gray-300' : 'text-gray-600'}`}>
            {i < step ? (
              <svg className="w-4 h-4 text-emerald-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : i === step ? (
              <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin flex-shrink-0" />
            ) : (
              <div className="w-4 h-4 rounded-full border border-gray-600 flex-shrink-0" />
            )}
            {s}
          </div>
        ))}
      </div>
    </div>
  )
}

export default function ATSAnalyzer() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [resumes, setResumes] = useState([])
  const [selectedResume, setSelectedResume] = useState(searchParams.get('resume') || '')
  const [analyzing, setAnalyzing] = useState(false)
  const [result, setResult] = useState(null)
  const [history, setHistory] = useState([])
  const [loadingResult, setLoadingResult] = useState(false)

  useEffect(() => {
    resumeService.list()
      .then((r) => {
        setResumes(r.data)
        if (!selectedResume && r.data.length > 0) {
          const active = r.data.find((x) => x.is_active)
          setSelectedResume(String(active?.id || r.data[0].id))
        }
      })
      .catch(() => {})
  }, [])

  // Load existing result when resume changes
  useEffect(() => {
    if (!selectedResume) return
    setLoadingResult(true)
    setResult(null)
    atsService.getResults(selectedResume)
      .then((r) => setResult(r.data))
      .catch(() => {}) // 404 = no result yet, that's fine
      .finally(() => setLoadingResult(false))

    atsService.getHistory(selectedResume)
      .then((r) => setHistory(r.data))
      .catch(() => {})
  }, [selectedResume])

  const handleAnalyze = async () => {
    if (!selectedResume) { toast.error('Select a resume first'); return }
    setAnalyzing(true)
    setResult(null)
    try {
      const { data } = await atsService.analyze(selectedResume)
      setResult(data)
      // Refresh history
      const h = await atsService.getHistory(selectedResume)
      setHistory(h.data)
      toast.success('Analysis complete!')
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Analysis failed')
    } finally {
      setAnalyzing(false)
    }
  }

  const chartData = history.map((h, i) => ({
    name: `v${h.version_number || i + 1}`,
    'Overall Score': h.overall_score,
    'Structure': h.structure_score,
    'Keywords': h.keyword_score,
    'Skills': h.skills_score,
  }))

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">ATS Score Analyzer</h1>
        <p className="text-gray-400 text-sm mt-1">Check how well your resume passes automated screening</p>
      </div>

      {/* Controls */}
      <div className="flex flex-col sm:flex-row gap-3 p-4 rounded-xl bg-white/3 border border-white/8">
        <div className="flex-1">
          <label className="block text-xs text-gray-500 mb-1.5">Select Resume</label>
          <select
            value={selectedResume}
            onChange={(e) => setSelectedResume(e.target.value)}
            className="w-full bg-gray-800 border border-white/10 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-blue-500"
          >
            <option value="">-- Choose a resume --</option>
            {resumes.map((r) => (
              <option key={r.id} value={r.id}>{r.title}{r.is_active ? ' (Active)' : ''}</option>
            ))}
          </select>
        </div>
        <div className="flex items-end gap-2">
          <button
            onClick={handleAnalyze}
            disabled={analyzing || !selectedResume}
            className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-medium text-sm disabled:opacity-40 disabled:cursor-not-allowed transition-all"
          >
            {analyzing ? 'Analyzing…' : 'Analyze Now'}
          </button>
          {selectedResume && (
            <button
              onClick={() => navigate(`/ats/job-specific?resume=${selectedResume}`)}
              className="px-4 py-2.5 rounded-xl border border-white/10 text-gray-300 text-sm hover:bg-white/5"
            >
              Job-Specific
            </button>
          )}
        </div>
      </div>

      {/* Analyzing state */}
      {analyzing && <AnalyzingState />}

      {/* Loading existing result */}
      {loadingResult && !analyzing && (
        <div className="flex justify-center py-8">
          <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
        </div>
      )}

      {/* Results */}
      {result && !analyzing && (
        <div className="space-y-6">
          {/* Overall score card */}
          <div className="flex flex-col sm:flex-row items-center gap-8 p-6 rounded-2xl bg-gradient-to-br from-gray-800/80 to-gray-900/80 border border-white/10">
            <ScoreCircle score={result.overall_score} size={140} strokeWidth={10} />
            <div className="text-center sm:text-left">
              <p className="text-gray-400 text-sm mb-1">Overall ATS Score</p>
              <p className={`text-4xl font-bold ${getScoreColor(result.overall_score)}`}>
                {Math.round(result.overall_score)}
                <span className="text-xl text-gray-500">/100</span>
              </p>
              <p className={`text-lg font-semibold mt-1 ${getScoreColor(result.overall_score)}`}>
                {getScoreLabel(result.overall_score)}
              </p>
              <p className="text-gray-500 text-sm mt-2">
                Analyzed {new Date(result.created_at).toLocaleString()}
              </p>
            </div>
          </div>

          {/* Sub-scores */}
          <div className="p-5 rounded-xl bg-white/3 border border-white/8">
            <h2 className="text-white font-semibold mb-4">Score Breakdown</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {SUB_SCORES.map(({ key, label, color }) => (
                <ProgressBar
                  key={key}
                  label={label}
                  value={result[key]}
                  color={color}
                  size="md"
                  showValue={true}
                />
              ))}
            </div>
          </div>

          {/* Score breakdown mini-circles */}
          <div className="grid grid-cols-3 sm:grid-cols-5 lg:grid-cols-9 gap-3">
            {SUB_SCORES.map(({ key, label }) => (
              <ScoreCircle key={key} score={result[key]} label={label} size={70} strokeWidth={6} />
            ))}
          </div>

          {/* Recommendations */}
          {result.recommendations && result.recommendations.length > 0 && (
            <div>
              <h2 className="text-white font-semibold mb-4">
                Recommendations
                <span className="ml-2 text-xs font-normal text-gray-400 px-2 py-0.5 rounded-full bg-white/8">
                  {result.recommendations.length} items
                </span>
              </h2>
              <div className="space-y-3">
                {result.recommendations.map((rec, i) => (
                  <ATSRecommendationCard key={i} recommendation={rec} />
                ))}
              </div>
            </div>
          )}

          {/* Improvement history chart */}
          {chartData.length > 1 && (
            <div className="p-5 rounded-xl bg-white/3 border border-white/8">
              <h2 className="text-white font-semibold mb-4">Score Improvement History</h2>
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 12 }} />
                  <YAxis domain={[0, 100]} tick={{ fill: '#9ca3af', fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1f2937',
                      border: '1px solid rgba(255,255,255,0.1)',
                      borderRadius: '8px',
                      color: '#f9fafb',
                    }}
                  />
                  <Legend wrapperStyle={{ color: '#9ca3af', fontSize: 12 }} />
                  <Line type="monotone" dataKey="Overall Score" stroke="#3b82f6" strokeWidth={2} dot={{ r: 4 }} />
                  <Line type="monotone" dataKey="Structure" stroke="#8b5cf6" strokeWidth={1.5} dot={{ r: 3 }} />
                  <Line type="monotone" dataKey="Keywords" stroke="#10b981" strokeWidth={1.5} dot={{ r: 3 }} />
                  <Line type="monotone" dataKey="Skills" stroke="#f59e0b" strokeWidth={1.5} dot={{ r: 3 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}

      {/* No result yet */}
      {!result && !analyzing && !loadingResult && selectedResume && (
        <div className="text-center py-12 rounded-xl border border-dashed border-white/10 bg-white/3">
          <div className="w-14 h-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mx-auto mb-3">
            <svg className="w-6 h-6 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <p className="text-gray-400 mb-3">No analysis results yet for this resume</p>
          <button
            onClick={handleAnalyze}
            className="px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium"
          >
            Run Analysis Now
          </button>
        </div>
      )}
    </div>
  )
}
