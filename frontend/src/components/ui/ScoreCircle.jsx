import { useMemo } from 'react'

function getColor(score) {
  if (score >= 80) return { stroke: '#10b981', text: '#10b981' } // green
  if (score >= 60) return { stroke: '#3b82f6', text: '#3b82f6' } // blue
  if (score >= 40) return { stroke: '#f59e0b', text: '#f59e0b' } // amber
  return { stroke: '#ef4444', text: '#ef4444' }                   // red
}

export default function ScoreCircle({ score = 0, label, size = 100, strokeWidth = 7 }) {
  const radius = (size - strokeWidth * 2) / 2
  const circumference = 2 * Math.PI * radius
  const offset = useMemo(
    () => circumference - (Math.min(100, Math.max(0, score)) / 100) * circumference,
    [score, circumference]
  )
  const { stroke, text } = getColor(score)

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          {/* Track */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="rgba(255,255,255,0.07)"
            strokeWidth={strokeWidth}
          />
          {/* Progress */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={stroke}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 0.8s ease' }}
          />
        </svg>
        {/* Score text */}
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-lg font-bold" style={{ color: text }}>
            {Math.round(score)}
          </span>
        </div>
      </div>
      {label && (
        <span className="text-xs text-gray-400 text-center leading-tight max-w-[80px]">{label}</span>
      )}
    </div>
  )
}
