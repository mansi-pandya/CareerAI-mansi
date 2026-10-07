import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import Card from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Button from '../../components/ui/Button'
import ProgressBar from '../../components/ui/ProgressBar'
import CareerService from '../../services/career.service'

const DEMAND_LABEL = (score) => {
  if (score >= 9) return { label: 'Very High', color: 'green' }
  if (score >= 7) return { label: 'High', color: 'blue' }
  if (score >= 5) return { label: 'Medium', color: 'yellow' }
  return { label: 'Low', color: 'red' }
}

export default function CareerDetail() {
  const { slug } = useParams()
  const navigate = useNavigate()
  const [career, setCareer] = useState(null)
  const [gap, setGap] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!slug) return
    Promise.all([
      CareerService.getCareer(slug),
      CareerService.getSkillGap(slug).catch(() => null),
    ])
      .then(([c, g]) => {
        setCareer(c)
        setGap(g)
      })
      .catch(() => toast.error('Failed to load career details'))
      .finally(() => setLoading(false))
  }, [slug])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="w-10 h-10 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (!career) {
    return (
      <div className="text-center py-16 text-gray-400">
        <div className="text-4xl mb-3">🔍</div>
        <p>Career not found.</p>
        <Button className="mt-4" variant="outline" onClick={() => navigate('/careers')}>← Back</Button>
      </div>
    )
  }

  const demand = DEMAND_LABEL(career.market_demand_score)

  return (
    <div className="space-y-6 max-w-5xl">
      {/* Back */}
      <button
        onClick={() => navigate('/careers')}
        className="text-sm text-gray-400 hover:text-white flex items-center gap-1 transition-colors"
      >
        ← Back to Recommendations
      </button>

      {/* Hero */}
      <Card>
        <Card.Body>
          <div className="flex items-start justify-between gap-4 flex-wrap">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <Badge variant="indigo">{career.industry}</Badge>
                <Badge variant={demand.color}>{demand.label} Demand</Badge>
              </div>
              <h1 className="text-2xl font-bold text-white">{career.name}</h1>
              <p className="text-gray-300 mt-2 text-sm leading-relaxed max-w-2xl">
                {career.description}
              </p>
            </div>
            {gap && (
              <div className="text-center min-w-[100px]">
                <div className="text-4xl font-bold text-blue-400">{gap.match_percentage}%</div>
                <div className="text-xs text-gray-400 mt-1">Your Match</div>
              </div>
            )}
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-white/6">
            <Stat label="Avg Salary" value={`$${(career.avg_salary_min / 1000).toFixed(0)}k – $${(career.avg_salary_max / 1000).toFixed(0)}k`} />
            <Stat label="Market Demand" value={`${career.market_demand_score}/10`} />
            <Stat label="Growth Rate" value={`+${career.growth_rate}%`} sub="per year" />
            <Stat label="Skills Required" value={career.required_skills?.length || 0} sub="core skills" />
          </div>
        </Card.Body>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Required skills */}
        <Card>
          <Card.Header>
            <h2 className="text-sm font-semibold text-white">Required Skills</h2>
          </Card.Header>
          <Card.Body className="space-y-3">
            {(career.required_skills || []).map((skill) => {
              const matched = gap?.matched_skills?.some((m) => m.skill_name === skill)
              return (
                <div key={skill} className="flex items-center justify-between gap-2">
                  <span className="text-sm text-gray-200 capitalize">{skill}</span>
                  {matched ? (
                    <span className="text-emerald-400 text-xs font-medium flex items-center gap-1">
                      ✓ You have it
                    </span>
                  ) : (
                    <span className="text-orange-400 text-xs font-medium flex items-center gap-1">
                      ⚠ Missing
                    </span>
                  )}
                </div>
              )
            })}
          </Card.Body>
        </Card>

        {/* Preferred skills */}
        <Card>
          <Card.Header>
            <h2 className="text-sm font-semibold text-white">Preferred Skills</h2>
          </Card.Header>
          <Card.Body>
            <div className="flex flex-wrap gap-2">
              {(career.preferred_skills || []).map((skill) => (
                <Badge key={skill} variant="default">{skill}</Badge>
              ))}
            </div>
          </Card.Body>
        </Card>
      </div>

      {/* Skill gap summary */}
      {gap && (
        <Card>
          <Card.Header>
            <h2 className="text-sm font-semibold text-white">Your Skill Gap</h2>
          </Card.Header>
          <Card.Body className="space-y-4">
            <ProgressBar
              value={gap.match_percentage}
              label={`${gap.matched_count} of ${gap.total_required} skills matched`}
              color={gap.match_percentage >= 70 ? 'green' : gap.match_percentage >= 40 ? 'yellow' : 'red'}
              size="lg"
            />
            {gap.missing_skills?.length > 0 && (
              <div>
                <p className="text-xs text-gray-400 mb-2">Top skills to learn:</p>
                <div className="flex flex-wrap gap-2">
                  {gap.missing_skills.slice(0, 6).map((s) => (
                    <span key={s.skill_name} className="px-2 py-0.5 bg-orange-900/30 border border-orange-500/20 rounded-full text-orange-300 text-xs capitalize">
                      {s.skill_name}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </Card.Body>
        </Card>
      )}

      {/* Action buttons */}
      <div className="flex gap-3 flex-wrap">
        <Button onClick={() => navigate(`/skill-gap?career=${slug}`)}>
          Full Skill Gap Analysis
        </Button>
        <Button variant="secondary" onClick={() => navigate(`/learning/roadmap?career=${slug}`)}>
          View Learning Roadmap
        </Button>
        <Button variant="outline" onClick={() => navigate('/improvement')}>
          Improvement Center
        </Button>
      </div>
    </div>
  )
}

function Stat({ label, value, sub }) {
  return (
    <div>
      <div className="text-lg font-bold text-white">{value}</div>
      {sub && <div className="text-xs text-gray-500">{sub}</div>}
      <div className="text-xs text-gray-400 mt-0.5">{label}</div>
    </div>
  )
}
