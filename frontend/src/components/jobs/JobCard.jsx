import { Link } from 'react-router-dom'
import { clsx } from 'clsx'
import Badge from '../ui/Badge'

const JOB_TYPE_COLORS = {
  internship: 'purple',
  full_time: 'green',
  part_time: 'blue',
  freelance: 'orange',
  contract: 'yellow',
  apprenticeship: 'teal',
}

const WORK_MODE_COLORS = {
  remote: 'green',
  hybrid: 'blue',
  on_site: 'default',
}

const JOB_TYPE_LABELS = {
  internship: 'Internship',
  full_time: 'Full-time',
  part_time: 'Part-time',
  freelance: 'Freelance',
  contract: 'Contract',
  apprenticeship: 'Apprenticeship',
}

const WORK_MODE_LABELS = {
  remote: 'Remote',
  hybrid: 'Hybrid',
  on_site: 'On-site',
}

function ScoreBadge({ score }) {
  if (score == null) return null
  const pct = Math.round(score * 100)
  const color =
    pct >= 75 ? 'text-emerald-400' : pct >= 50 ? 'text-yellow-400' : 'text-gray-400'
  return (
    <span className={clsx('text-xs font-semibold tabular-nums', color)}>
      {pct}% match
    </span>
  )
}

function formatDate(dateStr) {
  if (!dateStr) return null
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now - date
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  if (diffDays < 7) return `${diffDays}d ago`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`
  return `${Math.floor(diffDays / 30)}mo ago`
}

function formatSalary(min, max, currency) {
  if (!min && !max) return null
  const fmt = (n) => {
    if (currency === 'INR') {
      if (n >= 100000) return `₹${(n / 100000).toFixed(1)}L`
      return `₹${(n / 1000).toFixed(0)}K`
    }
    if (n >= 1000) return `$${(n / 1000).toFixed(0)}K`
    return `$${n}`
  }
  if (min && max) return `${fmt(min)} – ${fmt(max)}`
  if (min) return `${fmt(min)}+`
  return `Up to ${fmt(max)}`
}

export default function JobCard({ job, onSave, onUnsave, compact = false }) {
  const {
    id,
    title,
    company,
    location,
    job_type,
    work_mode,
    salary_min,
    salary_max,
    salary_currency,
    required_skills = [],
    posted_date,
    source_name,
    is_demo,
    overall_score,
    is_saved,
  } = job

  const visibleSkills = required_skills.slice(0, 4)
  const extraSkills = required_skills.length - 4

  const handleSaveClick = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (is_saved) onUnsave?.(id)
    else onSave?.(id)
  }

  return (
    <Link to={`/jobs/${id}`} className="block group">
      <div
        className={clsx(
          'bg-gray-900 border border-white/6 rounded-xl transition-all duration-200',
          'hover:border-white/15 hover:bg-gray-800/70',
          compact ? 'p-4' : 'p-5',
        )}
      >
        {/* Header row */}
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <h3
                className={clsx(
                  'font-semibold text-white truncate',
                  compact ? 'text-sm' : 'text-base',
                )}
              >
                {title}
              </h3>
              {is_demo && (
                <span className="text-[10px] text-yellow-500/70 border border-yellow-500/30 rounded px-1 py-0.5 shrink-0">
                  Demo
                </span>
              )}
            </div>
            <p className="text-sm text-gray-400 truncate">{company}</p>
          </div>

          {/* Save + score */}
          <div className="flex flex-col items-end gap-1 shrink-0">
            <ScoreBadge score={overall_score} />
            <button
              onClick={handleSaveClick}
              className={clsx(
                'p-1.5 rounded-lg transition-colors',
                is_saved
                  ? 'text-blue-400 hover:text-blue-300'
                  : 'text-gray-500 hover:text-gray-300',
              )}
              title={is_saved ? 'Unsave job' : 'Save job'}
            >
              <svg className="w-4 h-4" fill={is_saved ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M17 3H7a2 2 0 00-2 2v16l7-3 7 3V5a2 2 0 00-2-2z" />
              </svg>
            </button>
          </div>
        </div>

        {/* Location & type badges */}
        <div className="flex items-center gap-2 flex-wrap mt-2">
          {location && (
            <span className="flex items-center gap-1 text-xs text-gray-400">
              <svg className="w-3 h-3 shrink-0" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              {location}
            </span>
          )}
          {job_type && (
            <Badge variant={JOB_TYPE_COLORS[job_type] || 'default'}>
              {JOB_TYPE_LABELS[job_type] || job_type}
            </Badge>
          )}
          {work_mode && (
            <Badge variant={WORK_MODE_COLORS[work_mode] || 'default'}>
              {WORK_MODE_LABELS[work_mode] || work_mode}
            </Badge>
          )}
        </div>

        {/* Salary */}
        {(salary_min || salary_max) && (
          <p className="text-xs text-emerald-400/80 mt-2">
            {formatSalary(salary_min, salary_max, salary_currency)}
          </p>
        )}

        {/* Skills */}
        {visibleSkills.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-3">
            {visibleSkills.map((skill) => (
              <span
                key={skill}
                className="px-2 py-0.5 text-xs rounded-full bg-white/5 border border-white/10 text-gray-300"
              >
                {skill}
              </span>
            ))}
            {extraSkills > 0 && (
              <span className="px-2 py-0.5 text-xs rounded-full bg-white/5 border border-white/10 text-gray-500">
                +{extraSkills} more
              </span>
            )}
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between mt-3 pt-3 border-t border-white/5">
          <span className="text-[11px] text-gray-600">{formatDate(posted_date)}</span>
          {source_name && (
            <span className="text-[11px] text-gray-600">via {source_name}</span>
          )}
        </div>
      </div>
    </Link>
  )
}
