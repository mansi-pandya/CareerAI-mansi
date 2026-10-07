import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import Card from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Button from '../../components/ui/Button'
import SkillGapCard from '../../components/career/SkillGapCard'
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

export default function SkillGap() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const initialCareer = searchParams.get('career') || CAREERS[0].slug

  const [selectedCareer, setSelectedCareer] = useState(initialCareer)
  const [gap, setGap] = useState(null)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('missing')

  useEffect(() => {
    fetchGap(selectedCareer)
  }, [selectedCareer])

  async function fetchGap(slug) {
    setLoading(true)
    try {
      const data = await CareerService.getSkillGap(slug)
      setGap(data)
    } catch {
      toast.error('Failed to load skill gap analysis')
    } finally {
      setLoading(false)
    }
  }

  const priorityGroups = gap
    ? {
        high: gap.missing_skills.filter((s) => s.priority === 'high'),
        medium: gap.missing_skills.filter((s) => s.priority === 'medium'),
        low: gap.missing_skills.filter((s) => s.priority === 'low'),
      }
    : { high: [], medium: [], low: [] }

  return (
    <div className="space-y-6 max-w-5xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Skill Gap Analysis</h1>
        <p className="text-gray-400 text-sm mt-1">
          See exactly which skills you have and which ones you need for your target career.
        </p>
      </div>

      {/* Career selector */}
      <Card>
        <Card.Body>
          <label className="block text-sm font-medium text-gray-300 mb-2">Target Career</label>
          <select
            value={selectedCareer}
            onChange={(e) => setSelectedCareer(e.target.value)}
            className="w-full md:w-80 bg-gray-800 border border-white/10 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-blue-500"
          >
            {CAREERS.map((c) => (
              <option key={c.slug} value={c.slug}>{c.name}</option>
            ))}
          </select>
        </Card.Body>
      </Card>

      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
        </div>
      )}

      {!loading && gap && (
        <>
          {/* Summary */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <SummaryCard label="Match" value={`${gap.match_percentage}%`} color="blue" />
            <SummaryCard label="Skills You Have" value={gap.matched_count} color="green" />
            <SummaryCard label="Skills Missing" value={gap.missing_count} color="orange" />
            <SummaryCard
              label="High Priority Gaps"
              value={priorityGroups.high.length}
              color="red"
            />
          </div>

          {/* Overall progress bar */}
          <Card>
            <Card.Body>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-300 font-medium">Overall Skill Coverage</span>
                <span className="text-sm font-bold text-white">{gap.match_percentage}%</span>
              </div>
              <div className="w-full h-3 bg-white/8 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-700"
                  style={{
                    width: `${gap.match_percentage}%`,
                    background: gap.match_percentage >= 70
                      ? '#10b981'
                      : gap.match_percentage >= 40
                        ? '#f59e0b'
                        : '#ef4444',
                  }}
                />
              </div>
              <p className="text-xs text-gray-500 mt-2">
                {gap.matched_count} of {gap.total_required} skills matched for {gap.career_name}
              </p>
            </Card.Body>
          </Card>

          {/* Tabs */}
          <div className="flex gap-1 bg-gray-800/60 p-1 rounded-xl w-fit">
            {[
              { key: 'missing', label: `Missing (${gap.missing_count})` },
              { key: 'matched', label: `You Have (${gap.matched_count})` },
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  activeTab === tab.key
                    ? 'bg-blue-600 text-white shadow'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Missing skills */}
          {activeTab === 'missing' && (
            <div className="space-y-6">
              {priorityGroups.high.length > 0 && (
                <PrioritySection title="🔴 High Priority" skills={priorityGroups.high} navigate={navigate} />
              )}
              {priorityGroups.medium.length > 0 && (
                <PrioritySection title="🟡 Medium Priority" skills={priorityGroups.medium} navigate={navigate} />
              )}
              {priorityGroups.low.length > 0 && (
                <PrioritySection title="🟢 Lower Priority" skills={priorityGroups.low} navigate={navigate} />
              )}
              {gap.missing_count === 0 && (
                <Card>
                  <Card.Body className="text-center py-8">
                    <div className="text-3xl mb-2">🎉</div>
                    <p className="text-white font-semibold">You have all required skills!</p>
                    <p className="text-gray-400 text-sm mt-1">You're ready to apply for {gap.career_name} roles.</p>
                  </Card.Body>
                </Card>
              )}
            </div>
          )}

          {/* Matched skills */}
          {activeTab === 'matched' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {gap.matched_skills.map((skill) => (
                <SkillGapCard key={skill.skill_name} skill={skill} matched />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}

function SummaryCard({ label, value, color }) {
  const colors = {
    blue: 'text-blue-400',
    green: 'text-emerald-400',
    orange: 'text-orange-400',
    red: 'text-red-400',
  }
  return (
    <Card>
      <Card.Body className="text-center py-4">
        <div className={`text-3xl font-bold ${colors[color]}`}>{value}</div>
        <div className="text-xs text-gray-400 mt-1">{label}</div>
      </Card.Body>
    </Card>
  )
}

function PrioritySection({ title, skills, navigate }) {
  return (
    <div>
      <h3 className="text-sm font-semibold text-gray-300 mb-3">{title}</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {skills.map((skill) => (
          <SkillGapCard
            key={skill.skill_name}
            skill={skill}
            onViewResources={() =>
              navigate(`/learning?skill=${encodeURIComponent(skill.skill_name)}`)
            }
          />
        ))}
      </div>
    </div>
  )
}
