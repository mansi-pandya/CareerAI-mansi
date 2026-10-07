import ScoreCircle from '../ui/ScoreCircle'
import ProgressBar from '../ui/ProgressBar'

const SUB_SCORES = [
  { key: 'structure_score', label: 'Structure', color: 'blue' },
  { key: 'formatting_score', label: 'Formatting', color: 'indigo' },
  { key: 'keyword_score', label: 'Keywords', color: 'purple' },
  { key: 'skills_score', label: 'Skills', color: 'teal' },
  { key: 'projects_score', label: 'Projects', color: 'green' },
  { key: 'experience_score', label: 'Experience', color: 'blue' },
  { key: 'education_score', label: 'Education', color: 'orange' },
  { key: 'contact_score', label: 'Contact Info', color: 'yellow' },
  { key: 'job_alignment_score', label: 'Job Alignment', color: 'indigo' },
]

function getLabel(score) {
  if (score >= 80) return { text: 'Excellent', cls: 'text-emerald-400' }
  if (score >= 65) return { text: 'Good', cls: 'text-blue-400' }
  if (score >= 45) return { text: 'Needs Work', cls: 'text-amber-400' }
  return { text: 'Poor', cls: 'text-red-400' }
}

/**
 * Reusable ATS score breakdown card.
 *
 * Props:
 *   score   — ATSScore object from API (with all score fields)
 *   compact — show compact version (no sub-circles, just bars)
 */
export default function ResumeScoreCard({ score, compact = false }) {
  if (!score) return null

  const { text, cls } = getLabel(score.overall_score)

  return (
    <div className="p-5 rounded-2xl bg-white/3 border border-white/10 space-y-5">
      {/* Overall */}
      <div className="flex items-center gap-5">
        <ScoreCircle score={score.overall_score} size={90} strokeWidth={8} />
        <div>
          <p className="text-gray-400 text-xs mb-0.5">Overall ATS Score</p>
          <p className={`text-3xl font-bold ${cls}`}>{Math.round(score.overall_score)}</p>
          <p className={`text-sm font-medium ${cls}`}>{text}</p>
        </div>
      </div>

      {/* Sub-scores */}
      <div className="space-y-2.5">
        {SUB_SCORES.map(({ key, label, color }) => (
          <ProgressBar
            key={key}
            label={label}
            value={score[key]}
            color={color}
            size="sm"
            showValue
          />
        ))}
      </div>

      {/* Mini circles (non-compact only) */}
      {!compact && (
        <div className="flex flex-wrap gap-3 justify-around pt-1">
          {SUB_SCORES.map(({ key, label }) => (
            <ScoreCircle key={key} score={score[key]} label={label} size={60} strokeWidth={5} />
          ))}
        </div>
      )}
    </div>
  )
}
