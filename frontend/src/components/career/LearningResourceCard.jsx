import Badge from '../ui/Badge'

const DIFFICULTY_BADGE = {
  beginner: { variant: 'green', label: 'Beginner' },
  intermediate: { variant: 'yellow', label: 'Intermediate' },
  advanced: { variant: 'red', label: 'Advanced' },
}

export default function LearningResourceCard({ resource }) {
  const diff = DIFFICULTY_BADGE[resource.difficulty] || DIFFICULTY_BADGE.beginner

  return (
    <div className="rounded-xl border border-white/6 bg-gray-900 p-5 flex flex-col h-full hover:border-white/15 transition-all duration-200">
      {/* Top: provider + free/paid + difficulty */}
      <div className="flex items-center gap-2 flex-wrap mb-3">
        <Badge variant="indigo">{resource.provider}</Badge>
        <Badge variant={diff.variant}>{diff.label}</Badge>
        <Badge variant={resource.is_free ? 'green' : 'default'}>
          {resource.is_free ? '🆓 Free' : '💳 Paid'}
        </Badge>
      </div>

      {/* Skill tag */}
      <div className="text-xs text-blue-400 font-medium mb-1 capitalize">
        {resource.skill_name}
      </div>

      {/* Title */}
      <h3 className="text-white font-semibold text-sm leading-snug mb-1">
        {resource.resource_name}
      </h3>

      {/* Description */}
      {resource.description && (
        <p className="text-gray-400 text-xs leading-relaxed mb-3 line-clamp-2">
          {resource.description}
        </p>
      )}

      {/* Topics */}
      {resource.topics?.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-3">
          {resource.topics.slice(0, 5).map((t) => (
            <span
              key={t}
              className="text-xs text-gray-400 bg-white/4 border border-white/5 px-2 py-0.5 rounded-full"
            >
              {t}
            </span>
          ))}
          {resource.topics.length > 5 && (
            <span className="text-xs text-gray-500">+{resource.topics.length - 5}</span>
          )}
        </div>
      )}

      {/* Why recommended */}
      {resource.why_recommended && (
        <div className="rounded-lg bg-blue-900/10 border border-blue-500/15 px-3 py-2 mb-3">
          <p className="text-blue-300 text-xs leading-relaxed">
            <span className="font-medium">Why recommended: </span>
            {resource.why_recommended}
          </p>
        </div>
      )}

      {/* Footer: duration + link */}
      <div className="mt-auto pt-3 border-t border-white/6 flex items-center justify-between gap-2">
        {resource.duration_hours > 0 && (
          <span className="text-xs text-gray-500">
            ⏱ {resource.duration_hours}h
          </span>
        )}
        <a
          href={resource.url}
          target="_blank"
          rel="noopener noreferrer"
          className="ml-auto inline-flex items-center gap-1.5 text-xs text-blue-400 hover:text-blue-300 font-medium underline underline-offset-2"
        >
          Visit Resource
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>
      </div>
    </div>
  )
}
