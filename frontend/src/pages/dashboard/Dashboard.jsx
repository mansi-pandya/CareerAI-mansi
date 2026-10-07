import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  DocumentPlusIcon,
  ArrowUpTrayIcon,
  ChartBarIcon,
  BriefcaseIcon,
  ShieldCheckIcon,
  MicrophoneIcon,
  AcademicCapIcon,
  ArrowRightIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'
import api from '../../services/api'
import { useAuth } from '../../hooks/useAuth'
import ScoreCircle from '../../components/ui/ScoreCircle'
import Card from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Button from '../../components/ui/Button'

const ICON_MAP = {
  DocumentPlusIcon,
  ArrowUpTrayIcon,
  ChartBarIcon,
  BriefcaseIcon,
  ShieldCheckIcon,
  MicrophoneIcon,
  AcademicCapIcon,
}

const ACTION_COLORS = {
  blue: 'from-blue-600/20 to-blue-800/20 border-blue-500/20 hover:border-blue-400/40',
  indigo: 'from-indigo-600/20 to-indigo-800/20 border-indigo-500/20 hover:border-indigo-400/40',
  purple: 'from-purple-600/20 to-purple-800/20 border-purple-500/20 hover:border-purple-400/40',
  green: 'from-emerald-600/20 to-emerald-800/20 border-emerald-500/20 hover:border-emerald-400/40',
  teal: 'from-teal-600/20 to-teal-800/20 border-teal-500/20 hover:border-teal-400/40',
  orange: 'from-orange-600/20 to-orange-800/20 border-orange-500/20 hover:border-orange-400/40',
  red: 'from-red-600/20 to-red-800/20 border-red-500/20 hover:border-red-400/40',
}

const ICON_COLORS = {
  blue: 'text-blue-400',
  indigo: 'text-indigo-400',
  purple: 'text-purple-400',
  green: 'text-emerald-400',
  teal: 'text-teal-400',
  orange: 'text-orange-400',
  red: 'text-red-400',
}

function ScoreCard({ label, value, color }) {
  return (
    <div className="glass rounded-xl p-4 flex flex-col items-center gap-2 hover:border-white/15 transition-all">
      <ScoreCircle score={value} size={80} strokeWidth={6} />
      <span className="text-xs text-gray-400 text-center">{label}</span>
    </div>
  )
}

function QuickAction({ action }) {
  const IconComponent = ICON_MAP[action.icon] || BriefcaseIcon
  const colorClass = ACTION_COLORS[action.color] || ACTION_COLORS.blue
  const iconColor = ICON_COLORS[action.color] || 'text-blue-400'

  return (
    <Link to={action.href}>
      <div className={`bg-gradient-to-br ${colorClass} border rounded-xl p-4 flex flex-col items-center gap-3 text-center transition-all duration-200 cursor-pointer hover:scale-105`}>
        <IconComponent className={`w-7 h-7 ${iconColor}`} />
        <span className="text-xs font-medium text-gray-300">{action.label}</span>
      </div>
    </Link>
  )
}

export default function Dashboard() {
  const { user } = useAuth()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const res = await api.get('/dashboard/')
        setData(res.data)
      } catch (err) {
        toast.error('Failed to load dashboard')
      } finally {
        setLoading(false)
      }
    }
    fetchDashboard()
  }, [])

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[400px]">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  const scores = data?.scores || {}
  const scoreItems = [
    { label: 'ATS Readiness', value: scores.ats_readiness ?? 0 },
    { label: 'Skill Match', value: scores.skill_match ?? 0 },
    { label: 'Career Match', value: scores.career_match ?? 0 },
    { label: 'Job Match', value: scores.job_match ?? 0 },
    { label: 'Interview Ready', value: scores.interview_readiness ?? 0 },
    { label: 'Overall', value: scores.overall ?? 0 },
  ]

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-8 max-w-7xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">
            Welcome back, {user?.full_name?.split(' ')[0]} 👋
          </h1>
          <p className="text-gray-400 mt-1">
            {data?.profile_complete
              ? 'Your career readiness dashboard is up to date.'
              : 'Complete your profile to unlock personalized insights.'}
          </p>
        </div>
        {!data?.profile_complete && (
          <Link to="/profile">
            <Button variant="primary" size="sm">
              <SparklesIcon className="w-4 h-4" />
              Complete Profile
            </Button>
          </Link>
        )}
      </div>

      {/* Career Readiness Scores */}
      <section>
        <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
          Career Readiness Scores
        </h2>
        <div className="grid grid-cols-3 sm:grid-cols-6 gap-3">
          {scoreItems.map((s) => (
            <ScoreCard key={s.label} label={s.label} value={s.value} />
          ))}
        </div>
      </section>

      {/* Quick Actions */}
      {data?.quick_actions && (
        <section>
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
            Quick Actions
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
            {data.quick_actions.map((action) => (
              <QuickAction key={action.id} action={action} />
            ))}
          </div>
        </section>
      )}

      {/* Three-column grid: Careers | Jobs | Skill Gaps */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Recommended Careers */}
        <Card className="lg:col-span-1">
          <Card.Header>
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-white">Recommended Careers</h3>
              <Link to="/careers" className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1">
                View all <ArrowRightIcon className="w-3 h-3" />
              </Link>
            </div>
          </Card.Header>
          <Card.Body className="px-0 py-0">
            {data?.recommended_careers?.length ? (
              <ul className="divide-y divide-white/5">
                {data.recommended_careers.slice(0, 5).map((c, i) => (
                  <li key={i} className="flex items-center justify-between px-6 py-3 hover:bg-white/3 transition-colors">
                    <div>
                      <p className="text-sm font-medium text-white">{c.title}</p>
                      <p className="text-xs text-gray-500">{c.industry} · {c.avg_salary}</p>
                    </div>
                    <Badge variant={c.match >= 80 ? 'green' : c.match >= 60 ? 'blue' : 'default'}>
                      {c.match}%
                    </Badge>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="px-6 py-8 text-center">
                <p className="text-gray-500 text-sm">Complete your profile to see career recommendations.</p>
                <Link to="/profile" className="mt-3 inline-block">
                  <Button size="sm" variant="outline">Complete Profile</Button>
                </Link>
              </div>
            )}
          </Card.Body>
        </Card>

        {/* Skill Gaps */}
        <Card className="lg:col-span-1">
          <Card.Header>
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-white">Skill Gaps</h3>
              <Link to="/skills" className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1">
                View all <ArrowRightIcon className="w-3 h-3" />
              </Link>
            </div>
          </Card.Header>
          <Card.Body className="px-0 py-0">
            {data?.skill_gaps?.length ? (
              <ul className="divide-y divide-white/5">
                {data.skill_gaps.slice(0, 5).map((s, i) => (
                  <li key={i} className="flex items-center justify-between px-6 py-3 hover:bg-white/3 transition-colors">
                    <div>
                      <p className="text-sm font-medium text-white">{s.skill}</p>
                      <p className="text-xs text-gray-500">{s.resources} resources available</p>
                    </div>
                    <Badge variant={s.importance === 'High' ? 'red' : s.importance === 'Medium' ? 'yellow' : 'default'}>
                      {s.importance}
                    </Badge>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="px-6 py-8 text-center">
                <p className="text-gray-500 text-sm">Upload your resume to identify skill gaps.</p>
              </div>
            )}
          </Card.Body>
        </Card>

        {/* Recommended Jobs */}
        <Card className="lg:col-span-1">
          <Card.Header>
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-white">Recommended Jobs</h3>
              <Link to="/jobs" className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1">
                View all <ArrowRightIcon className="w-3 h-3" />
              </Link>
            </div>
          </Card.Header>
          <Card.Body className="px-0 py-0">
            {data?.recommended_jobs?.length ? (
              <ul className="divide-y divide-white/5">
                {data.recommended_jobs.slice(0, 5).map((j, i) => (
                  <li key={i} className="px-6 py-3 hover:bg-white/3 transition-colors">
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-white truncate">{j.title}</p>
                        <p className="text-xs text-gray-500">{j.company} · {j.location}</p>
                        <div className="flex items-center gap-2 mt-1.5">
                          <Badge variant="default" className="text-xs">{j.type}</Badge>
                          <span className="text-xs text-gray-600">{j.posted}</span>
                        </div>
                      </div>
                      <Badge variant={j.match >= 80 ? 'green' : j.match >= 60 ? 'blue' : 'default'} className="shrink-0">
                        {j.match}%
                      </Badge>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="px-6 py-8 text-center">
                <p className="text-gray-500 text-sm">Complete your profile to see job matches.</p>
              </div>
            )}
          </Card.Body>
        </Card>
      </div>
    </div>
  )
}
