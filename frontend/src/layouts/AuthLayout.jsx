import { Outlet, Link } from 'react-router-dom'
import { BriefcaseIcon } from '@heroicons/react/24/outline'

export default function AuthLayout() {
  return (
    <div className="min-h-screen flex flex-col bg-gray-950">
      {/* Header */}
      <header className="px-6 py-4 border-b border-white/5">
        <Link to="/" className="flex items-center gap-2 w-fit">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
            <BriefcaseIcon className="w-4 h-4 text-white" />
          </div>
          <span className="text-xl font-bold gradient-text">CareerAI</span>
        </Link>
      </header>

      {/* Content */}
      <div className="flex-1 flex items-center justify-center px-4 py-12">
        <Outlet />
      </div>

      {/* Footer */}
      <footer className="px-6 py-4 text-center text-xs text-gray-600 border-t border-white/5">
        © {new Date().getFullYear()} CareerAI · All rights reserved
      </footer>
    </div>
  )
}
