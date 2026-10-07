import ProgressBar from '../ui/ProgressBar'

const SCORE_ITEMS = [
  { key: 'skill_score', label: 'Skills Match', color: 'blue', weight: '40%' },
  { key: 'role_score', label: 'Role Alignment', color: 'indigo', weight: '20%' },
  { key: 'education_score', label: 'Education Fit', color: 'purple', weight: '15%' },
  { key: 'experience_score', label: 'Experience Level', color: 'teal', weight: '10%' },
  { key: 'location_score', label: 'Location / Work Mode', color: 'green', weight: '10%' },
  { key: 'preference_score', label: 'Career Preference', color: 'orange', weight: '5%' },
]

function OverallRing({ score }) {
  const pct = Math.round((score || 0) * 100)
  const color =
    pct >= 75
      ? 'text-emerald-400'
      : pct >= 50
        ? 'text-yellow-400'
        : pct >= 25
          ? 'text-orange-400'
          : 'text-gray-400'

  return (
    <div className="flex flex-col items-center gap-1">
      <div className={`text-4xl font-bold tabular-nums ${color}`}>{pct}%</div>
      <div className="text-xs text-gray-500">Overall Match</div>
    </div>
  )
}

export default function JobMatchBreakdown({ match }) {
  if (!match) return null

  const {
    overall_score,
    skill_score,
    role_score,
    education_score,
    experience_score,
    location_score,
    preference_score,
    match_reasons = [],
  } = match

  const scores = {
    skill_score,
    role_score,
    education_score,
    experience_score,
    location_score,
    preference_score,
  }

  return (
    <div className="space-y-5">
      {/* Overall */}
      <div className="flex items-center gap-6 p-4 rounded-xl bg-white/3 border border-white/8">
        <OverallRing score={overall_score} />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-200 mb-1">Match Score</p>
          <p className="text-xs text-gray-500 leading-relaxed">
            Based on your skills, experience, education, and career preferences compared to
            this job&apos;s requirements.
          </p>
        </div>
      </div>

      {/* Sub-scores */}
      <div className="space-y-3">
        {SCORE_ITEMS.map(({ key, label, color, weight }) => (
          <div key={key}>
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-gray-400">{label}</span>
              <span className="text-[11px] text-gray-600">{weight}</span>
            </div>
            <ProgressBar
              value={Math.round((scores[key] || 0) * 100)}
              max={100}
              color={color}
              showValue
              size="sm"
            />
          </div>
        ))}
      </div>

      {/* Reasons */}
      {match_reasons.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs font-semibold uppercase tracking-wider text-gray-500">
            Why this job?
          </p>
          <ul className="space-y-1.5">
            {match_reasons.map((reason, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                <span className="text-emerald-400 mt-0.5 shrink-0">✓</span>
                {reason}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
