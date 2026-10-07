import Badge from '../ui/Badge'
import Button from '../ui/Button'
import ProgressBar from '../ui/ProgressBar'

const RANK_COLORS = ['text-yellow-400', 'text-gray-300', 'text-amber-600', 'text-gray-400', 'text-gray-400']
const RANK_LABELS = ['🥇', '🥈', '🥉', '4th', '5th']

function matchColor(score) {
  if (score >= 80) return 'text-emerald-400'
  if (score >= 60) return 'text-blue-400'
  if (score >= 40) return 'text-yellow-400'
  return 'text-red-400'
}

function matchBarColor(score) {
  if (score >= 80) return 'green'
  if (score >= 60) return 'blue'
  if (score >= 40) return 'yellow'
  return 'red'
}

export default function CareerMatchCard({ match, rank, isSelected, onClick, onViewPath }) {
  const score = match.match_score || 0

  return (
    <div
      onClick={onClick}
      className={`rounded-xl border p-5 transition-all duration-200 cursor-pointer ${
        isSelected
          ? 'border-blue-500/50 bg-blue-900/10 shadow-lg shadow-blue-900/10'
          : 'border-white/6 bg-gray-900 hover:border-white/15 hover:bg-gray-800/70'
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        {/* Left: rank + info */}
        <div className="flex items-start gap-3">
          <span className="text-xl shrink-0 mt-0.5" aria-label={`Rank ${rank}`}>
            {RANK_LABELS[rank - 1] || `${rank}th`}
          </span>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="text-white font-semibold">{match.career_name}</h3>
              <Badge variant="default" className="text-xs">{match.career_industry}</Badge>
            </div>
            {match.career_description && (
              <p className="text-gray-400 text-xs mt-1 line-clamp-2">{match.career_description}</p>
            )}
          </div>
        </div>

        {/* Right: match score */}
        <div className="text-right shrink-0">
          <div className={`text-3xl font-bold ${matchColor(score)}`}>{score.toFixed(0)}%</div>
          <div className="text-xs text-gray-500">match</div>
        </div>
      </div>

      {/* Progress bar */}
      <div className="mt-3">
        <ProgressBar
          value={score}
          color={matchBarColor(score)}
          showValue={false}
          size="sm"
        />
      </div>

      {/* Salary + demand */}
      {(match.avg_salary_min > 0 || match.market_demand_score > 0) && (
        <div className="flex items-center gap-4 mt-3 text-xs text-gray-400">
          {match.avg_salary_min > 0 && (
            <span>💰 ${(match.avg_salary_min / 1000).toFixed(0)}k–${(match.avg_salary_max / 1000).toFixed(0)}k</span>
          )}
          {match.market_demand_score > 0 && (
            <span>📈 {match.market_demand_score}/10 demand</span>
          )}
          {match.growth_rate > 0 && (
            <span>🚀 +{match.growth_rate}% growth</span>
          )}
        </div>
      )}

      {/* Matched / missing pills */}
      <div className="mt-3 flex gap-3 flex-wrap">
        {match.matched_skills?.slice(0, 3).map((s) => (
          <span key={s} className="text-xs text-emerald-400 bg-emerald-900/20 border border-emerald-500/20 px-2 py-0.5 rounded-full">
            ✓ {s}
          </span>
        ))}
        {match.missing_skills?.slice(0, 2).map((s) => (
          <span key={s} className="text-xs text-orange-400 bg-orange-900/20 border border-orange-500/20 px-2 py-0.5 rounded-full">
            ⚠ {s}
          </span>
        ))}
        {(match.matched_skills?.length > 3 || match.missing_skills?.length > 2) && (
          <span className="text-xs text-gray-500">…more</span>
        )}
      </div>

      {/* Action */}
      <div className="mt-4 flex gap-2">
        <Button
          size="sm"
          onClick={(e) => { e.stopPropagation(); onViewPath?.() }}
        >
          View Career Path →
        </Button>
      </div>
    </div>
  )
}
