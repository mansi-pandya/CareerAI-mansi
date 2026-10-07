import { clsx } from 'clsx'

const colorMap = {
  blue: 'bg-blue-500',
  indigo: 'bg-indigo-500',
  purple: 'bg-purple-500',
  green: 'bg-emerald-500',
  red: 'bg-red-500',
  yellow: 'bg-yellow-500',
  teal: 'bg-teal-500',
  orange: 'bg-orange-500',
}

export default function ProgressBar({
  value = 0,
  max = 100,
  color = 'blue',
  label,
  showValue = true,
  size = 'md',
  className = '',
}) {
  const percent = Math.min(100, Math.max(0, (value / max) * 100))

  const heights = {
    xs: 'h-1',
    sm: 'h-1.5',
    md: 'h-2',
    lg: 'h-3',
  }

  return (
    <div className={clsx('w-full', className)}>
      {(label || showValue) && (
        <div className="flex items-center justify-between mb-1.5">
          {label && <span className="text-sm text-gray-400">{label}</span>}
          {showValue && (
            <span className="text-sm font-medium text-gray-300">{Math.round(percent)}%</span>
          )}
        </div>
      )}
      <div className={clsx('w-full bg-white/8 rounded-full overflow-hidden', heights[size])}>
        <div
          className={clsx('h-full rounded-full transition-all duration-700 ease-out', colorMap[color] || 'bg-blue-500')}
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  )
}
