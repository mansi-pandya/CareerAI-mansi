import Button from '../ui/Button'
import Badge from '../ui/Badge'

const IMPORTANCE_BADGE = {
  critical: { variant: 'red', label: 'Critical' },
  important: { variant: 'yellow', label: 'Important' },
  'nice-to-have': { variant: 'default', label: 'Nice to Have' },
}

const PRIORITY_CONFIG = {
  high: { border: 'border-red-500/25', bg: 'bg-red-900/10', dot: 'bg-red-500' },
  medium: { border: 'border-yellow-500/25', bg: 'bg-yellow-900/10', dot: 'bg-yellow-400' },
  low: { border: 'border-emerald-500/25', bg: 'bg-emerald-900/10', dot: 'bg-emerald-500' },
}

function LevelBar({ current, required, max = 5 }) {
  return (
    <div className="flex items-center gap-1">
      {Array.from({ length: max }).map((_, i) => (
        <div
          key={i}
          className={`w-4 h-1.5 rounded-sm ${
            i < required
              ? i < current
                ? 'bg-blue-500'
                : 'bg-gray-600'
              : 'bg-white/5'
          }`}
        />
      ))}
    </div>
  )
}

// ── Matched skill variant ─────────────────────────────────────────────────────
function MatchedSkillCard({ skill }) {
  const imp = IMPORTANCE_BADGE[skill.importance] || IMPORTANCE_BADGE.important
  return (
    <div className="rounded-xl border border-white/6 bg-gray-900 p-4">
      <div className="flex items-start justify-between gap-2 mb-2">
        <span className="text-sm text-white font-medium capitalize flex items-center gap-1.5">
          <span className="text-emerald-400">✓</span>
          {skill.skill_name}
        </span>
        <Badge variant={imp.variant}>{imp.label}</Badge>
      </div>
      <div className="space-y-1">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>Your level</span>
          <span className="text-white font-medium">{skill.current_level}/5</span>
        </div>
        <LevelBar current={skill.current_level} required={skill.required_level} />
        <div className="text-xs text-gray-500 capitalize">{skill.proficiency}</div>
      </div>
    </div>
  )
}

// ── Missing skill (gap) variant ───────────────────────────────────────────────
function GapSkillCard({ skill, onViewResources }) {
  const imp = IMPORTANCE_BADGE[skill.importance] || IMPORTANCE_BADGE.important
  const pri = PRIORITY_CONFIG[skill.priority] || PRIORITY_CONFIG.medium

  return (
    <div className={`rounded-xl border p-4 ${pri.border} ${pri.bg}`}>
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full shrink-0 mt-1 ${pri.dot}`} />
          <span className="text-sm text-white font-medium capitalize">{skill.skill_name}</span>
        </div>
        <div className="flex gap-1.5">
          <Badge variant={imp.variant}>{imp.label}</Badge>
          <Badge variant="default">{skill.priority} priority</Badge>
        </div>
      </div>

      <div className="space-y-2 mt-2">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>Current → Required</span>
          <span className="text-orange-300 font-medium">Gap: {skill.gap}</span>
        </div>
        <div className="space-y-0.5">
          <div className="text-xs text-gray-500">Current ({skill.current_level}/5)</div>
          <LevelBar current={skill.current_level} required={skill.required_level} />
          <div className="text-xs text-gray-500">Required: {skill.required_level}/5</div>
        </div>
      </div>

      {onViewResources && (
        <Button
          size="xs"
          variant="outline"
          className="mt-3"
          onClick={onViewResources}
        >
          View Learning Resources
        </Button>
      )}
    </div>
  )
}

// ── Exported component — auto-selects variant ─────────────────────────────────
export default function SkillGapCard({ skill, matched, onViewResources }) {
  if (matched) return <MatchedSkillCard skill={skill} />
  return <GapSkillCard skill={skill} onViewResources={onViewResources} />
}
