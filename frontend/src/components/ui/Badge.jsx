import { clsx } from 'clsx'

const variants = {
  default: 'bg-gray-800 text-gray-300 border border-white/10',
  blue: 'bg-blue-900/40 text-blue-300 border border-blue-500/30',
  indigo: 'bg-indigo-900/40 text-indigo-300 border border-indigo-500/30',
  purple: 'bg-purple-900/40 text-purple-300 border border-purple-500/30',
  green: 'bg-emerald-900/40 text-emerald-300 border border-emerald-500/30',
  red: 'bg-red-900/40 text-red-300 border border-red-500/30',
  yellow: 'bg-yellow-900/40 text-yellow-300 border border-yellow-500/30',
  teal: 'bg-teal-900/40 text-teal-300 border border-teal-500/30',
  orange: 'bg-orange-900/40 text-orange-300 border border-orange-500/30',
}

export default function Badge({ children, variant = 'default', className = '', ...props }) {
  return (
    <span
      className={clsx(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
        variants[variant],
        className,
      )}
      {...props}
    >
      {children}
    </span>
  )
}
