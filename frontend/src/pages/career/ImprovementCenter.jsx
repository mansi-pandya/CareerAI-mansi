import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import Card from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Button from '../../components/ui/Button'
import CareerService from '../../services/career.service'

const PRIORITY_CONFIG = {
  high: { label: 'HIGH PRIORITY', bg: 'bg-red-900/20', border: 'border-red-500/30', dot: 'bg-red-500', text: 'text-red-400' },
  medium: { label: 'MEDIUM', bg: 'bg-yellow-900/20', border: 'border-yellow-500/30', dot: 'bg-yellow-400', text: 'text-yellow-400' },
  low: { label: 'LOW', bg: 'bg-emerald-900/20', border: 'border-emerald-500/30', dot: 'bg-emerald-500', text: 'text-emerald-400' },
}

export default function ImprovementCenter() {
  const navigate = useNavigate()
  const [gaps, setGaps] = useState([])
  const [progress, setProgress] = useState([])
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      CareerService.getLearningResources().catch(() => []),
      CareerService.getProgress().catch(() => []),
      CareerService.getRecommendations().catch(() => []),
    ])
      .then(([resources, prog, recs]) => {
        setGaps(resources)
        setProgress(prog)
        setRecommendations(recs)
      })
      .catch(() => toast.error('Failed to load improvement data'))
      .finally(() => setLoading(false))
  }, [])

  // Build improvement items from skill gaps + resources
  const improvementItems = []
  const seenSkills = new Set()

  gaps.forEach((r) => {
    if (!seenSkills.has(r.skill_name)) {
      seenSkills.add(r.skill_name)
      const prog = progress.find((p) => p.skill_name.toLowerCase() === r.skill_name.toLowerCase())
      improvementItems.push({
        type: 'skill',
        skill_name: r.skill_name,
        priority: r.importance === 'critical' ? 'high' : 'medium',
        why: `This skill is ${r.importance} for your target career path.`,
        action: `Learn ${r.skill_name} using the resources in the Learning Center.`,
        resource_name: r.resource_name,
        resource_url: r.url,
        provider: r.provider,
        current_progress: prog?.proficiency_level || 0,
      })
    }
  })

  // Top career to focus on
  const topCareer = recommendations[0]

  // Missing skills from top career recommendation
  const resumeItems = topCareer?.missing_skills?.slice(0, 3).map((skill) => ({
    type: 'resume',
    skill_name: skill,
    priority: 'high',
    why: `Adding "${skill}" to your resume would improve your match for ${topCareer.career_name}.`,
    action: 'Add this skill to your profile after completing relevant coursework or projects.',
    resource_url: null,
  })) || []

  const allItems = [
    ...improvementItems.filter((i) => i.priority === 'high'),
    ...resumeItems,
    ...improvementItems.filter((i) => i.priority === 'medium'),
    ...improvementItems.filter((i) => i.priority === 'low'),
  ].slice(0, 20)

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="w-10 h-10 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-5xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">CareerAI Improvement Center</h1>
        <p className="text-gray-400 text-sm mt-1">
          Personalized actions to improve your career readiness, ranked by impact.
        </p>
      </div>

      {/* Top career focus */}
      {topCareer && (
        <div className="rounded-xl border border-blue-500/20 bg-blue-900/10 px-5 py-4 flex items-center justify-between gap-4 flex-wrap">
          <div>
            <div className="text-xs text-blue-400 font-medium mb-1">TOP CAREER MATCH</div>
            <div className="text-white font-semibold text-lg">{topCareer.career_name}</div>
            <div className="text-gray-400 text-sm">{topCareer.match_score?.toFixed(0)}% match · {topCareer.career_industry}</div>
          </div>
          <Button
            size="sm"
            onClick={() => navigate(`/careers/${topCareer.career_slug}`)}
          >
            View Path →
          </Button>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <StatCard value={improvementItems.filter((i) => i.priority === 'high').length} label="High Priority Items" color="text-red-400" />
        <StatCard value={improvementItems.filter((i) => i.priority === 'medium').length} label="Medium Priority" color="text-yellow-400" />
        <StatCard value={progress.filter((p) => p.proficiency_level >= 50).length} label="Skills In Progress" color="text-emerald-400" />
      </div>

      {/* Improvement items */}
      {allItems.length === 0 ? (
        <Card>
          <Card.Body className="text-center py-12">
            <div className="text-4xl mb-3">🎉</div>
            <h3 className="text-white font-semibold mb-2">No improvements needed right now!</h3>
            <p className="text-gray-400 text-sm">Complete your profile and add skills to get personalized recommendations.</p>
            <Button className="mt-4" onClick={() => navigate('/profile')}>Complete Profile</Button>
          </Card.Body>
        </Card>
      ) : (
        <>
          {/* Sections */}
          <Section
            title="Skill Gaps"
            items={allItems.filter((i) => i.type === 'skill')}
            navigate={navigate}
          />
          {resumeItems.length > 0 && (
            <Section
              title="Resume & Profile Improvements"
              items={allItems.filter((i) => i.type === 'resume')}
              navigate={navigate}
              isResume
            />
          )}
          {progress.length > 0 && (
            <div>
              <h2 className="text-sm font-semibold text-white mb-3">Learning Progress</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {progress.map((p) => (
                  <Card key={p.skill_name}>
                    <Card.Body className="py-3">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-white capitalize">{p.skill_name}</span>
                        <span className="text-xs text-gray-400">{p.proficiency_level}%</span>
                      </div>
                      <div className="w-full h-1.5 bg-white/8 rounded-full">
                        <div
                          className="h-full rounded-full bg-blue-500 transition-all"
                          style={{ width: `${p.proficiency_level}%` }}
                        />
                      </div>
                    </Card.Body>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}

function Section({ title, items, navigate, isResume }) {
  if (!items.length) return null
  return (
    <div>
      <h2 className="text-sm font-semibold text-white mb-3">{title}</h2>
      <div className="space-y-3">
        {items.map((item, i) => {
          const cfg = PRIORITY_CONFIG[item.priority] || PRIORITY_CONFIG.medium
          return (
            <div
              key={i}
              className={`rounded-xl border p-4 ${cfg.bg} ${cfg.border}`}
            >
              <div className="flex items-start justify-between gap-3 flex-wrap">
                <div className="flex items-start gap-3">
                  <div className={`w-2.5 h-2.5 rounded-full mt-1.5 shrink-0 ${cfg.dot}`} />
                  <div>
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <span className={`text-xs font-bold ${cfg.text}`}>{cfg.label}</span>
                      <span className="text-white font-medium text-sm capitalize">{item.skill_name}</span>
                      {item.provider && <Badge variant="default">{item.provider}</Badge>}
                    </div>
                    <p className="text-gray-300 text-xs mb-1">{item.why}</p>
                    <p className="text-gray-400 text-xs italic">{item.action}</p>
                    {item.current_progress > 0 && (
                      <div className="flex items-center gap-2 mt-2">
                        <div className="w-20 h-1 bg-white/10 rounded-full">
                          <div
                            className="h-full rounded-full bg-blue-500"
                            style={{ width: `${item.current_progress}%` }}
                          />
                        </div>
                        <span className="text-xs text-gray-400">{item.current_progress}% complete</span>
                      </div>
                    )}
                  </div>
                </div>
                {item.resource_url && (
                  <a
                    href={item.resource_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="shrink-0 text-xs text-blue-400 hover:text-blue-300 underline underline-offset-2"
                  >
                    {item.resource_name || 'View Resource'} →
                  </a>
                )}
                {isResume && !item.resource_url && (
                  <Button size="xs" variant="outline" onClick={() => navigate('/profile')}>
                    Update Profile
                  </Button>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function StatCard({ value, label, color }) {
  return (
    <Card>
      <Card.Body className="text-center py-4">
        <div className={`text-3xl font-bold ${color}`}>{value}</div>
        <div className="text-xs text-gray-400 mt-1">{label}</div>
      </Card.Body>
    </Card>
  )
}
