import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import Card from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Button from '../../components/ui/Button'
import CareerService from '../../services/career.service'

const CAREERS = [
  { slug: 'software-engineer', name: 'Software Engineer' },
  { slug: 'frontend-developer', name: 'Frontend Developer' },
  { slug: 'backend-developer', name: 'Backend Developer' },
  { slug: 'full-stack-developer', name: 'Full Stack Developer' },
  { slug: 'data-analyst', name: 'Data Analyst' },
  { slug: 'data-scientist', name: 'Data Scientist' },
  { slug: 'machine-learning-engineer', name: 'Machine Learning Engineer' },
  { slug: 'ai-engineer', name: 'AI Engineer' },
  { slug: 'cloud-engineer', name: 'Cloud Engineer' },
  { slug: 'devops-engineer', name: 'DevOps Engineer' },
  { slug: 'qa-engineer', name: 'QA Engineer' },
  { slug: 'mobile-developer', name: 'Mobile Developer' },
  { slug: 'cybersecurity-analyst', name: 'Cybersecurity Analyst' },
  { slug: 'product-manager', name: 'Product Manager' },
  { slug: 'ui-ux-designer', name: 'UI/UX Designer' },
]

const PHASE_COLORS = ['from-blue-600 to-indigo-600', 'from-purple-600 to-pink-600', 'from-teal-600 to-cyan-600', 'from-orange-600 to-amber-600']

export default function LearningRoadmap() {
  const [searchParams] = useSearchParams()
  const initialCareer = searchParams.get('career') || CAREERS[0].slug

  const [selectedCareer, setSelectedCareer] = useState(initialCareer)
  const [roadmap, setRoadmap] = useState(null)
  const [progress, setProgress] = useState({})
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [expandedPhases, setExpandedPhases] = useState(new Set([1]))

  // What-If state
  const [whatIfSkills, setWhatIfSkills] = useState([])
  const [whatIfResult, setWhatIfResult] = useState(null)
  const [loadingWhatIf, setLoadingWhatIf] = useState(false)

  useEffect(() => {
    fetchRoadmap(selectedCareer)
    loadProgress()
  }, [selectedCareer])

  async function loadProgress() {
    try {
      const prog = await CareerService.getProgress()
      const map = {}
      prog.forEach((p) => { map[p.skill_name.toLowerCase()] = p.proficiency_level })
      setProgress(map)
    } catch { /* silent */ }
  }

  async function fetchRoadmap(slug) {
    setLoading(true)
    setRoadmap(null)
    setWhatIfResult(null)
    try {
      const data = await CareerService.getRoadmap(slug)
      setRoadmap(data)
    } catch {
      toast.error('Failed to load roadmap')
    } finally {
      setLoading(false)
    }
  }

  async function handleGenerate() {
    setGenerating(true)
    try {
      const data = await CareerService.generateRoadmap(selectedCareer)
      setRoadmap(data)
      toast.success('Roadmap generated!')
    } catch {
      toast.error('Failed to generate roadmap')
    } finally {
      setGenerating(false)
    }
  }

  async function handleProgressUpdate(skillName, level) {
    setProgress((prev) => ({ ...prev, [skillName.toLowerCase()]: level }))
    try {
      await CareerService.updateProgress(skillName, level)
    } catch { /* silent */ }
  }

  async function runWhatIf() {
    if (!whatIfSkills.length) {
      toast.error('Select at least one skill')
      return
    }
    setLoadingWhatIf(true)
    try {
      const result = await CareerService.whatIf(selectedCareer, whatIfSkills)
      setWhatIfResult(result)
    } catch {
      toast.error('What-If simulation failed')
    } finally {
      setLoadingWhatIf(false)
    }
  }

  const togglePhase = (n) => {
    setExpandedPhases((prev) => {
      const s = new Set(prev)
      s.has(n) ? s.delete(n) : s.add(n)
      return s
    })
  }

  const allMissingSkills = roadmap?.phases?.flatMap((p) => p.skills_todo || []) || []

  return (
    <div className="space-y-6 max-w-5xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Learning Roadmap</h1>
        <p className="text-gray-400 text-sm mt-1">
          Phase-by-phase learning path tailored to your target career.
        </p>
      </div>

      {/* Career selector + generate */}
      <Card>
        <Card.Body>
          <div className="flex flex-wrap gap-3 items-end">
            <div className="flex-1 min-w-[200px]">
              <label className="block text-xs text-gray-400 mb-1">Target Career</label>
              <select
                value={selectedCareer}
                onChange={(e) => setSelectedCareer(e.target.value)}
                className="w-full bg-gray-800 border border-white/10 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-blue-500"
              >
                {CAREERS.map((c) => (
                  <option key={c.slug} value={c.slug}>{c.name}</option>
                ))}
              </select>
            </div>
            <Button
              variant="outline"
              size="sm"
              loading={generating}
              onClick={handleGenerate}
            >
              {roadmap ? '↻ Regenerate' : 'Generate Roadmap'}
            </Button>
          </div>
        </Card.Body>
      </Card>

      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
        </div>
      )}

      {!loading && roadmap && (
        <>
          {/* Overall progress */}
          <Card>
            <Card.Body>
              <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
                <div>
                  <h2 className="text-white font-semibold">{roadmap.title}</h2>
                  <p className="text-xs text-gray-400 mt-0.5">
                    {roadmap.total_weeks} weeks estimated · {roadmap.total_skills} skills total
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-blue-400">{roadmap.overall_progress}%</div>
                  <div className="text-xs text-gray-400">Overall Progress</div>
                </div>
              </div>
              <div className="w-full h-2.5 bg-white/8 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-blue-500 to-indigo-500 transition-all duration-700"
                  style={{ width: `${roadmap.overall_progress}%` }}
                />
              </div>
            </Card.Body>
          </Card>

          {/* Phases */}
          <div className="space-y-4">
            {roadmap.phases?.map((phase, phaseIdx) => (
              <Card key={phase.phase_number} className={phase.completed ? 'opacity-75' : ''}>
                {/* Phase header */}
                <button
                  className="w-full px-6 py-4 flex items-start justify-between gap-3 text-left"
                  onClick={() => togglePhase(phase.phase_number)}
                >
                  <div className="flex items-start gap-3">
                    <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${PHASE_COLORS[phaseIdx % 4]} flex items-center justify-center text-white text-sm font-bold shrink-0`}>
                      {phase.phase_number}
                    </div>
                    <div>
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-white font-semibold">{phase.phase_name}</span>
                        {phase.completed && <Badge variant="green">✓ Complete</Badge>}
                        <Badge variant="default">{phase.estimated_weeks}w</Badge>
                      </div>
                      <p className="text-gray-400 text-xs mt-0.5">{phase.description}</p>
                      {/* Progress bar */}
                      <div className="flex items-center gap-2 mt-1.5">
                        <div className="w-24 h-1.5 bg-white/10 rounded-full">
                          <div
                            className="h-full rounded-full bg-blue-500 transition-all"
                            style={{ width: `${phase.progress_pct}%` }}
                          />
                        </div>
                        <span className="text-xs text-gray-500">{phase.progress_pct}%</span>
                      </div>
                    </div>
                  </div>
                  <svg
                    className={`w-5 h-5 text-gray-400 transition-transform shrink-0 mt-1 ${expandedPhases.has(phase.phase_number) ? 'rotate-180' : ''}`}
                    fill="none" stroke="currentColor" viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {/* Expanded content */}
                {expandedPhases.has(phase.phase_number) && (
                  <div className="border-t border-white/6 px-6 py-4 space-y-5">
                    {phase.skills.map((skill) => {
                      const isDone = phase.skills_done?.includes(skill)
                      const currentLevel = progress[skill.toLowerCase()] || 0
                      const topics = phase.topics?.[skill] || []
                      const skillResources = phase.resources?.[skill] || []

                      return (
                        <div key={skill} className="space-y-2">
                          {/* Skill header */}
                          <div className="flex items-center justify-between gap-2">
                            <div className="flex items-center gap-2">
                              {isDone ? (
                                <span className="text-emerald-400">✓</span>
                              ) : (
                                <span className="text-gray-500">○</span>
                              )}
                              <span className="text-sm text-white font-medium capitalize">{skill}</span>
                              {isDone && <Badge variant="green" className="text-xs">You have it</Badge>}
                            </div>
                            {/* Progress input */}
                            <div className="flex items-center gap-2 shrink-0">
                              <span className="text-xs text-gray-400">{currentLevel}%</span>
                              <input
                                type="range"
                                min="0"
                                max="100"
                                step="5"
                                value={currentLevel}
                                onChange={(e) => handleProgressUpdate(skill, parseInt(e.target.value))}
                                className="w-20 accent-blue-500"
                              />
                            </div>
                          </div>

                          {/* Topics */}
                          {topics.length > 0 && (
                            <div className="ml-6 flex flex-wrap gap-1.5">
                              {topics.map((t) => (
                                <span key={t} className="text-xs text-gray-400 bg-white/4 px-2 py-0.5 rounded-full border border-white/5">
                                  {t}
                                </span>
                              ))}
                            </div>
                          )}

                          {/* Resources */}
                          {skillResources.length > 0 && (
                            <div className="ml-6 space-y-1.5">
                              {skillResources.map((res, ri) => (
                                <a
                                  key={ri}
                                  href={res.url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="flex items-center gap-2 text-xs text-blue-400 hover:text-blue-300 group"
                                >
                                  <span>{res.is_free ? '🆓' : '💳'}</span>
                                  <span className="underline underline-offset-1 group-hover:no-underline">{res.resource_name}</span>
                                  <span className="text-gray-500">· {res.provider}</span>
                                </a>
                              ))}
                            </div>
                          )}
                        </div>
                      )
                    })}
                  </div>
                )}
              </Card>
            ))}
          </div>

          {/* What-If Panel */}
          {allMissingSkills.length > 0 && (
            <Card>
              <Card.Header>
                <h2 className="text-sm font-semibold text-white">What If I Learn These Skills?</h2>
                <p className="text-xs text-gray-400 mt-0.5">
                  Simulate how your career match score would improve if you learned selected skills.
                </p>
              </Card.Header>
              <Card.Body className="space-y-4">
                {/* Skill checkboxes */}
                <div className="flex flex-wrap gap-2">
                  {allMissingSkills.slice(0, 15).map((skill) => {
                    const checked = whatIfSkills.includes(skill)
                    return (
                      <button
                        key={skill}
                        onClick={() =>
                          setWhatIfSkills((prev) =>
                            checked ? prev.filter((s) => s !== skill) : [...prev, skill]
                          )
                        }
                        className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                          checked
                            ? 'bg-indigo-600 border-indigo-500 text-white'
                            : 'bg-gray-800 border-white/10 text-gray-400 hover:text-white'
                        }`}
                      >
                        {checked ? '✓ ' : '+ '}{skill}
                      </button>
                    )
                  })}
                </div>

                <Button
                  size="sm"
                  loading={loadingWhatIf}
                  disabled={!whatIfSkills.length}
                  onClick={runWhatIf}
                >
                  Simulate
                </Button>

                {/* Result */}
                {whatIfResult && (
                  <div className="rounded-xl border border-indigo-500/20 bg-indigo-900/10 p-4 space-y-3">
                    <div className="flex items-center gap-6 flex-wrap">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-gray-300">{whatIfResult.current_match?.toFixed(0)}%</div>
                        <div className="text-xs text-gray-400">Current Match</div>
                      </div>
                      <div className="text-2xl text-gray-500">→</div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-indigo-400">{whatIfResult.estimated_match?.toFixed(0)}%</div>
                        <div className="text-xs text-gray-400">Estimated Match</div>
                      </div>
                      {whatIfResult.improvement > 0 && (
                        <Badge variant="indigo">+{whatIfResult.improvement?.toFixed(1)}% improvement</Badge>
                      )}
                    </div>
                    <p className="text-sm text-gray-300">{whatIfResult.explanation}</p>
                    <p className="text-xs text-gray-500 italic">{whatIfResult.disclaimer}</p>
                  </div>
                )}
              </Card.Body>
            </Card>
          )}
        </>
      )}
    </div>
  )
}
