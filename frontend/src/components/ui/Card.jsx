import { clsx } from 'clsx'

export default function Card({ children, className = '', glass = false, hover = false, ...props }) {
  return (
    <div
      className={clsx(
        'rounded-xl border',
        glass
          ? 'bg-white/4 border-white/8 backdrop-blur-sm'
          : 'bg-gray-900 border-white/6',
        hover && 'hover:border-white/15 hover:bg-gray-800/70 transition-all duration-200 cursor-pointer',
        className,
      )}
      {...props}
    >
      {children}
    </div>
  )
}

Card.Header = function CardHeader({ children, className = '' }) {
  return (
    <div className={clsx('px-6 py-4 border-b border-white/6', className)}>
      {children}
    </div>
  )
}

Card.Body = function CardBody({ children, className = '' }) {
  return (
    <div className={clsx('px-6 py-5', className)}>
      {children}
    </div>
  )
}

Card.Footer = function CardFooter({ children, className = '' }) {
  return (
    <div className={clsx('px-6 py-4 border-t border-white/6', className)}>
      {children}
    </div>
  )
}
