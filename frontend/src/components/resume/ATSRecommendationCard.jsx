import { useState } from 'react'

const PRIORITY_CONFIG = {
  high: {
    label: 'High Priority',
    border: 'border-red-500/30',
    bg: 'bg-red-900/10',
    badge: 'bg-red-900/40 text-red-300 border-red-500/30',
    dot: 'bg-red-500',
  },
  medium: {
    label: 'Medium Priority',
    border: 'border-amber-500/30',
    bg: 'bg-amber-900/10',
    badge: 'bg-amber-900/40 text-amber-300 border-amber-500/30',
    dot: 'bg-amber-500',
  },
  low: {
    label: 'Low Priority',
    border: 'border-blue-500/20',
    bg: 'bg-blue-900/5',
    badge: 'bg-blue-900/30 text-blue-300 border-blue-500/20',
    dot: 'bg-blue-500',
  },
}

/**
 * Card for a single ATS recommendation.
 *
 * Props:
 *   recommendation — ATSRecommendation object with fields:
 *     category, current_problem, why_it_matters, how_to_fix,
 *     section_to_modify, priority, estimated_score_impact
 */
export default function ATSRecommendationCard({ recommendation: rec }) {
  const [expanded, setExpanded] = useState(false)
  const cfg = PRIORITY_CONFIG[rec.priority] || PRIORITY_CONFIG.medium

  return (
    <div className={`rounded-xl border ${cfg.border} ${cfg.bg} overflow-hidden`}>
      {/* Header row */}
      <button
        onClick={() => setExpanded((v) => !v)}
        className="w-full flex items-start gap-3 p-4 text-left hover:bg-white/3 transition-colors"
      >
        {/* Priority dot */}
        <div className={`w-2.5 h-2.5 rounded-full ${cfg.dot} mt-1.5 flex-shrink-0`} />

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            {/* Category */}
            <span className="text-white text-sm font-medium">{rec.category}</span>
            {/* Priority badge */}
            <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${cfg.badge}`}>
              {cfg.label}
            </span>
            {/* Score impact */}
            {rec.estimated_score_impact > 0 && (
              <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-900/30 text-emerald-400 border border-emerald-500/20">
                +{rec.estimated_score_impact} pts
              </span>
            )}
            {/* Section tag */}
            {rec.section_to_modify && (
              <span className="text-xs text-gray-500 px-1.5 py-0.5 rounded bg-white/5 capitalize">
                {rec.section_to_modify}
              </span>
            )}
          </div>
          {/* Problem summary */}
          <p className="text-gray-400 text-xs mt-1 line-clamp-2">{rec.current_problem}</p>
        </div>

        {/* Expand chevron */}
        <svg
          className={`w-4 h-4 text-gray-500 flex-shrink-0 mt-0.5 transition-transform ${expanded ? 'rotate-180' : ''}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Expanded details */}
      {expanded && (
        <div className="px-4 pb-4 space-y-3 border-t border-white/5 pt-3">
          {/* Problem */}
          <div>
            <p className="text-xs font-semibold text-gray-400 mb-1 uppercase tracking-wide">Problem</p>
            <p className="text-gray-300 text-sm leading-relaxed">{rec.current_problem}</p>
          </div>

          {/* Why it matters */}
          <div className="p-3 rounded-lg bg-amber-900/10 border border-amber-500/10">
            <p className="text-xs font-semibold text-amber-400 mb-1 uppercase tracking-wide">Why It Matters</p>
            <p className="text-gray-300 text-sm leading-relaxed">{rec.why_it_matters}</p>
          </div>

          {/* How to fix */}
          <div className="p-3 rounded-lg bg-emerald-900/10 border border-emerald-500/10">
            <p className="text-xs font-semibold text-emerald-400 mb-1 uppercase tracking-wide">How to Fix</p>
            <p className="text-gray-300 text-sm leading-relaxed">{rec.how_to_fix}</p>
          </div>
        </div>
      )}
    </div>
  )
}
