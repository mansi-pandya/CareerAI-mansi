import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ResponsiveContainer, Tooltip,
} from 'recharts'
import interviewsService from '../../services/interviews.service'
import ScoreCircle from '../../components/ui/ScoreCircle'

const PRIORITY_STYLES = {
  high: {
    badge: 'bg-red-500/20 text-red-300 border-red-500/40',
    border: 'border-red-500/30',
    dot: 'bg-red-500',
    label: 'HIGH',
  },
  medium: {
    badge: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
    border: 'border-amber-500/30',
    dot: 'bg-amber-500',
    label: 'MEDIUM',
  },
  low: {
    badge: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
    border: 'border-emerald-500/30',
    dot: 'bg-emerald-500',
    label: 'LOW',
  },
}

const TYPE_COLORS = {
  technical: 'bg-blue-500/20 text-blue-300',
  coding: 'bg-purple-500/20 text-purple-300',
  behavioral: 'bg-amber-500/20 text-amber-300',
  hr: 'bg-emerald-500/20 text-emerald-300',
  project: 'bg-pink-500/20 text-pink-300',
}

function ScoreBar({ label, value }) {
  if (value == null) return null
  const color =
    value >= 80
      ? 'bg-emerald-500'
      : value >= 60
      ? 'bg-blue-500'
      : value >= 40
      ? 'bg-amber-500'
      : 'bg-red-500'

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-gray-400">
        <span>{label}</span>
        <span className="font-medium text-white">{Math.round(value)}</span>
      </div>
      <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
        <div
          className={`h-full ${color} rounded-full transition-all duration-700`}
          style={{ width: `${Math.min(100, value)}%` }}
        />
      </div>
    </div>
  )
}

function QuestionAccordion({ item, index }) {
  const [open, setOpen] = useState(false)
  const score = item.answer?.score
  const scoreColor =
    score == null
      ? 'text-gray-500'
      : score >= 80
      ? 'text-emerald-400'
      : score >= 60
      ? 'text-blue-400'
      : score >= 40
      ? 'text-amber-400'
      : 'text-red-400'
  const typeStyle = TYPE_COLORS[item.question_type] || 'bg-gray-500/20 text-gray-300'

  return (
    <div className="bg-gray-900 border border-white/10 rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between p-4 text-left hover:bg-white/5 transition"
      >
        <div className="flex items-center gap-3 min-w-0">
          <span className="text-xs text-gray-500 shrink-0">Q{index + 1}</span>
          <span
            className={`text-xs px-2 py-0.5 rounded-md shrink-0 ${typeStyle}`}
          >
            {item.question_type}
          </span>
          <span className="text-sm text-white truncate">{item.question_text}</span>
        </div>
        <div className="flex items-center gap-3 shrink-0 ml-3">
          {score != null && (
            <span className={`text-sm font-bold ${scoreColor}`}>{Math.round(score)}</span>
          )}
          {!item.answer && <span className="text-xs text-gray-600">Unanswered</span>}
          <span className="text-gray-600 text-sm">{open ? '▲' : '▼'}</span>
        </div>
      </button>

      {open && (
        <div className="border-t border-white/10 p-4 space-y-4">
          <div>
            <p className="text-xs font-medium text-gray-500 mb-1">QUESTION</p>
            <p className="text-sm text-white leading-relaxed">{item.question_text}</p>
          </div>

          {item.answer ? (
            <>
              <div>
                <p className="text-xs font-medium text-gray-500 mb-1">YOUR ANSWER</p>
                <p className="text-sm text-gray-300 leading-relaxed bg-gray-800 rounded-lg p-3">
                  {item.answer.answer_text || '(no text recorded)'}
                </p>
              </div>

              <div>
                <p className="text-xs font-medium text-gray-500 mb-1">FEEDBACK</p>
                <p className="text-sm text-gray-300 leading-relaxed">{item.answer.feedback}</p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                {item.answer.strengths?.length > 0 && (
                  <div>
                    <p className="text-xs text-emerald-400 font-medium mb-1">✅ Strengths</p>
                    {item.answer.strengths.map((s, i) => (
                      <p key={i} className="text-xs text-gray-400">• {s}</p>
                    ))}
                  </div>
                )}
                {item.answer.weaknesses?.length > 0 && (
                  <div>
                    <p className="text-xs text-amber-400 font-medium mb-1">⚠️ To Improve</p>
                    {item.answer.weaknesses.map((w, i) => (
                      <p key={i} className="text-xs text-gray-400">• {w}</p>
                    ))}
                  </div>
                )}
              </div>

              {item.answer.better_answer_example && (
                <div className="bg-blue-500/5 border border-blue-500/20 rounded-lg p-3">
                  <p className="text-xs text-blue-300 font-medium mb-1">💡 Hint</p>
                  <p className="text-xs text-gray-300">{item.answer.better_answer_example}</p>
                </div>
              )}
            </>
          ) : (
            <p className="text-sm text-gray-600 italic">This question was not answered.</p>
          )}
        </div>
      )}
    </div>
  )
}

export default function InterviewResults() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const res = await interviewsService.get(id)
        setData(res.data)
      } catch {
        toast.error('Could not load interview results.')
        navigate('/interview/history')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [id]) // eslint-disable-line react-hooks/exhaustive-deps

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (!data) return null

  const radarData = [
    { subject: 'Technical', value: data.technical_score ?? 50 },
    { subject: 'Communication', value: data.communication_score ?? 50 },
    { subject: 'Relevance', value: data.relevance_score ?? 50 },
    { subject: 'Problem Solving', value: data.problem_solving_score ?? 50 },
    { subject: 'Projects', value: data.project_knowledge_score ?? 50 },
    { subject: 'HR/Behavioral', value: data.hr_behavioral_score ?? 50 },
    { subject: 'Tech Accuracy', value: data.technical_accuracy_score ?? 50 },
  ]

  const overall = data.overall_score ?? 0
  const overallColor =
    overall >= 80
      ? 'text-emerald-400'
      : overall >= 60
      ? 'text-blue-400'
      : overall >= 40
      ? 'text-amber-400'
      : 'text-red-400'

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Interview Results</h1>
          <p className="text-sm text-gray-400 mt-0.5">
            {data.target_career}
            {data.target_role && ` · ${data.target_role}`} ·{' '}
            <span className="capitalize">{data.interview_type?.replace('_', ' ')}</span>
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => navigate('/interview')}
            className="text-sm px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white transition"
          >
            Practice Again
          </button>
          <button
            onClick={() => navigate('/interview/history')}
            className="text-sm px-4 py-2 rounded-lg border border-white/10 text-gray-300 hover:border-white/30 transition"
          >
            History
          </button>
        </div>
      </div>

      {/* Overall Score */}
      <div className="bg-gray-900 border border-white/10 rounded-xl p-6 flex flex-col sm:flex-row items-center gap-6">
        <div className="flex flex-col items-center">
          <ScoreCircle score={overall} size={120} strokeWidth={9} />
          <span className="text-xs text-gray-500 mt-2">Overall Score</span>
        </div>
        <div className="flex-1 space-y-3">
          <div>
            <p className={`text-2xl font-bold ${overallColor}`}>{Math.round(overall)}/100</p>
            <p className="text-sm text-gray-400 mt-1 leading-relaxed">
              {data.feedback_summary || 'Interview completed.'}
            </p>
          </div>
          <div className="flex gap-2 flex-wrap text-xs">
            <span className="bg-gray-800 px-2 py-1 rounded text-gray-400 capitalize">
              {data.difficulty}
            </span>
            <span className="bg-gray-800 px-2 py-1 rounded text-gray-400">
              {data.questions?.length || 0} questions
            </span>
            <span className="bg-gray-800 px-2 py-1 rounded text-gray-400">
              {data.questions?.filter((q) => q.answer).length || 0} answered
            </span>
          </div>
        </div>
      </div>

      {/* Score Dimensions */}
      <div className="grid sm:grid-cols-2 gap-6">
        {/* Radar chart */}
        <div className="bg-gray-900 border border-white/10 rounded-xl p-5">
          <h2 className="text-sm font-semibold text-white mb-4">Score Breakdown</h2>
          <ResponsiveContainer width="100%" height={220}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="rgba(255,255,255,0.08)" />
              <PolarAngleAxis
                dataKey="subject"
                tick={{ fill: '#9ca3af', fontSize: 10 }}
              />
              <PolarRadiusAxis
                domain={[0, 100]}
                tick={{ fill: '#6b7280', fontSize: 9 }}
                tickCount={4}
              />
              <Radar
                name="Score"
                dataKey="value"
                stroke="#3b82f6"
                fill="#3b82f6"
                fillOpacity={0.2}
                strokeWidth={2}
              />
              <Tooltip
                contentStyle={{
                  background: '#1f2937',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '8px',
                  fontSize: 12,
                  color: '#f9fafb',
                }}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* Score bars */}
        <div className="bg-gray-900 border border-white/10 rounded-xl p-5 space-y-3">
          <h2 className="text-sm font-semibold text-white mb-2">Dimension Scores</h2>
          <ScoreBar label="Technical Knowledge" value={data.technical_score} />
          <ScoreBar label="Communication" value={data.communication_score} />
          <ScoreBar label="Relevance" value={data.relevance_score} />
          <ScoreBar label="Problem Solving" value={data.problem_solving_score} />
          <ScoreBar label="Project Knowledge" value={data.project_knowledge_score} />
          <ScoreBar label="HR / Behavioral" value={data.hr_behavioral_score} />
          <ScoreBar label="Technical Accuracy" value={data.technical_accuracy_score} />
        </div>
      </div>

      {/* Improvement Areas */}
      {data.improvements?.length > 0 && (
        <section>
          <h2 className="text-base font-semibold text-white mb-4">
            Improvement Recommendations
          </h2>
          <div className="space-y-3">
            {data.improvements.map((imp) => {
              const st = PRIORITY_STYLES[imp.priority] || PRIORITY_STYLES.medium
              return (
                <div
                  key={imp.id}
                  className={`bg-gray-900 border ${st.border} rounded-xl p-5 space-y-3`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full ${st.dot}`} />
                      <span className="text-sm font-semibold text-white">{imp.area}</span>
                    </div>
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full border font-medium ${st.badge}`}
                    >
                      {st.label}
                    </span>
                  </div>

                  {imp.explanation && (
                    <p className="text-sm text-gray-300 leading-relaxed">{imp.explanation}</p>
                  )}

                  {imp.practice_suggestion && (
                    <div className="bg-gray-800 rounded-lg p-3">
                      <p className="text-xs font-medium text-blue-300 mb-1">📚 Practice</p>
                      <p className="text-xs text-gray-300 leading-relaxed">
                        {imp.practice_suggestion}
                      </p>
                    </div>
                  )}

                  {imp.learning_resource_url && (
                    <a
                      href={imp.learning_resource_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300"
                    >
                      🔗 Learning Resource ↗
                    </a>
                  )}
                </div>
              )
            })}
          </div>
        </section>
      )}

      {/* Question Breakdown */}
      <section>
        <h2 className="text-base font-semibold text-white mb-4">
          Question Breakdown
          <span className="ml-2 text-xs font-normal text-gray-500">
            (click to expand)
          </span>
        </h2>
        <div className="space-y-2">
          {data.questions?.map((q, i) => (
            <QuestionAccordion key={q.id} item={q} index={i} />
          ))}
        </div>
      </section>

      {/* Bottom actions */}
      <div className="flex gap-3 pt-2">
        <button
          onClick={() => navigate('/interview')}
          className="flex-1 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm transition"
        >
          Practice Again
        </button>
        <button
          onClick={() => navigate('/interview/history')}
          className="flex-1 py-3 rounded-xl border border-white/10 text-gray-300 hover:border-white/30 text-sm transition"
        >
          View History
        </button>
      </div>
    </div>
  )
}
