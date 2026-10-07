import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import {
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  Radar, ResponsiveContainer, Tooltip,
} from 'recharts'
import Card from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Button from '../../components/ui/Button'
import CareerMatchCard from '../../components/career/CareerMatchCard'
import CareerService from '../../services/career.service'

export default function CareerRecommendations() {
  const navigate = useNavigate()
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [selected, setSelected] = useState(null)

  useEffect(() => {
    fetchRecommendations()
  }, [])

  async function fetchRecommendations() {
    try {
      setLoading(true)
      const data = await CareerService.getRecommendations()
      setRecommendations(data)
      if (data.length > 0) setSelected(data[0])
    } catch {
      toast.error('Failed to load recommendations')
    } finally {
      setLoading(false)
    }
  }

  async function handleRefresh() {
    try {
      setRefreshing(true)
      const data = await CareerService.refreshRecommendations()
      setRecommendations(data)
      if (data.length > 0) setSelected(data[0])
      toast.success('Recommendations refreshed!')
    } catch {
      toast.error('Failed to refresh recommendations')
    } finally {
      setRefreshing(false)
    }
  }

  const radarData = selected
    ? [
        { subject: 'Skills', value: selected.skill_score || 0 },
        { subject: 'Education', value: selected.education_score || 0 },
        { subject: 'Projects', value: selected.project_score || 0 },
        { subject: 'Experience', value: selected.experience_score || 0 },
        { subject: 'Interest', value: selected.interest_score || 0 },
      ]
    : []

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="w-10 h-10 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold text-white">Career Recommendations</h1>
          <p className="text-gray-400 text-sm mt-1">
            AI-powered matches based on your skills, education, and interests.
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          loading={refreshing}
          onClick={handleRefresh}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </Button>
      </div>

      {/* Disclaimer */}
      <div className="rounded-lg border border-yellow-500/20 bg-yellow-900/10 px-4 py-3 flex gap-3">
        <span className="text-yellow-400 mt-0.5 shrink-0">⚠</span>
        <p className="text-yellow-200/80 text-sm">
          These recommendations are based on your current profile and do <strong>not</strong> predict future career success. Many factors beyond skills and education determine career outcomes.
        </p>
      </div>

      {recommendations.length === 0 ? (
        <Card>
          <Card.Body className="text-center py-12">
            <div className="text-4xl mb-3">🎯</div>
            <h3 className="text-white font-semibold mb-1">No recommendations yet</h3>
            <p className="text-gray-400 text-sm mb-4">Complete your profile and add skills to get personalized career matches.</p>
            <Button onClick={() => navigate('/profile')}>Complete Profile</Button>
          </Card.Body>
        </Card>
      ) : (
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          {/* Cards column */}
          <div className="xl:col-span-2 space-y-4">
            {recommendations.map((rec, idx) => (
              <CareerMatchCard
                key={rec.career_slug || idx}
                match={rec}
                rank={idx + 1}
                isSelected={selected?.career_slug === rec.career_slug}
                onClick={() => setSelected(rec)}
                onViewPath={() => navigate(`/careers/${rec.career_slug}`)}
              />
            ))}
          </div>

          {/* Detail panel */}
          {selected && (
            <div className="space-y-4">
              {/* Radar */}
              <Card>
                <Card.Header>
                  <h3 className="text-sm font-semibold text-white">Score Breakdown</h3>
                  <p className="text-xs text-gray-400 mt-0.5">{selected.career_name}</p>
                </Card.Header>
                <Card.Body>
                  <ResponsiveContainer width="100%" height={220}>
                    <RadarChart data={radarData}>
                      <PolarGrid stroke="rgba(255,255,255,0.08)" />
                      <PolarAngleAxis dataKey="subject" tick={{ fill: '#9ca3af', fontSize: 11 }} />
                      <PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} />
                      <Radar
                        name="Score"
                        dataKey="value"
                        stroke="#6366f1"
                        fill="#6366f1"
                        fillOpacity={0.25}
                        strokeWidth={2}
                      />
                      <Tooltip
                        contentStyle={{ background: '#1f2937', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 12 }}
                        formatter={(v) => [`${v.toFixed(0)}%`]}
                      />
                    </RadarChart>
                  </ResponsiveContainer>
                </Card.Body>
              </Card>

              {/* Matched skills */}
              {selected.matched_skills?.length > 0 && (
                <Card>
                  <Card.Header>
                    <h3 className="text-sm font-semibold text-emerald-400">✓ You have these skills</h3>
                  </Card.Header>
                  <Card.Body>
                    <div className="flex flex-wrap gap-2">
                      {selected.matched_skills.map((s) => (
                        <Badge key={s} variant="green">{s}</Badge>
                      ))}
                    </div>
                  </Card.Body>
                </Card>
              )}

              {/* Missing skills */}
              {selected.missing_skills?.length > 0 && (
                <Card>
                  <Card.Header>
                    <h3 className="text-sm font-semibold text-orange-400">⚠ Skills to develop</h3>
                  </Card.Header>
                  <Card.Body>
                    <div className="flex flex-wrap gap-2">
                      {selected.missing_skills.slice(0, 8).map((s) => (
                        <Badge key={s} variant="orange">{s}</Badge>
                      ))}
                    </div>
                  </Card.Body>
                </Card>
              )}

              {/* Reasoning */}
              {selected.reasoning && (
                <Card>
                  <Card.Header>
                    <h3 className="text-sm font-semibold text-white">Why this career?</h3>
                  </Card.Header>
                  <Card.Body>
                    <p className="text-gray-300 text-sm leading-relaxed">{selected.reasoning}</p>
                  </Card.Body>
                </Card>
              )}

              <Button
                className="w-full"
                onClick={() => navigate(`/careers/${selected.career_slug}`)}
              >
                View Full Career Path →
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
