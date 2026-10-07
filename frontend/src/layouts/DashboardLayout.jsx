import { Outlet, Link, useLocation } from 'react-router-dom'
import { useState } from 'react'
import {
  HomeIcon,
  UserCircleIcon,
  DocumentTextIcon,
  BriefcaseIcon,
  AcademicCapIcon,
  ChartBarIcon,
  ShieldCheckIcon,
  VideoCameraIcon,
  MagnifyingGlassIcon,
  Bars3Icon,
  XMarkIcon,
  ArrowRightOnRectangleIcon,
} from '@heroicons/react/24/outline'
import { useAuth } from '../hooks/useAuth'
import { clsx } from 'clsx'

const NAV_ITEMS = [
  { label: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { label: 'Profile', href: '/profile', icon: UserCircleIcon },
  { label: 'Resume Builder', href: '/resume', icon: DocumentTextIcon },
  { label: 'ATS Checker', href: '/ats', icon: ChartBarIcon },
  { label: 'Career Matches', href: '/careers', icon: BriefcaseIcon },
  { label: 'Skill Gap', href: '/skill-gap', icon: AcademicCapIcon },
  { label: 'Learning Paths', href: '/learning', icon: ChartBarIcon },
  { label: 'Roadmap', href: '/learning/roadmap', icon: ShieldCheckIcon },
  { label: 'Improvement', href: '/improvement', icon: AcademicCapIcon },
  { label: 'Jobs', href: '/jobs', icon: BriefcaseIcon },
  { label: 'Opportunity Check', href: '/opportunity', icon: MagnifyingGlassIcon },
  { label: 'AI Interview', href: '/interview', icon: VideoCameraIcon },
]

function SidebarLink({ item, collapsed, onClick }) {
  const location = useLocation()
  const active = location.pathname === item.href || location.pathname.startsWith(item.href + '/')
  const Icon = item.icon

  return (
    <Link
      to={item.href}
      onClick={onClick}
      className={clsx(
        'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150',
        active
          ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
          : 'text-gray-400 hover:text-white hover:bg-white/5',
      )}
    >
      <Icon className="w-5 h-5 shrink-0" />
      {!collapsed && <span>{item.label}</span>}
    </Link>
  )
}

export default function DashboardLayout() {
  const [collapsed, setCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const { user, logout } = useAuth()

  return (
    <div className="flex min-h-screen bg-gray-950">
      {/* Sidebar — desktop */}
      <aside
        className={clsx(
          'hidden lg:flex flex-col border-r border-white/5 bg-gray-900 transition-all duration-300',
          collapsed ? 'w-16' : 'w-64',
        )}
      >
        {/* Logo */}
        <div className="flex items-center justify-between px-4 py-5 border-b border-white/5">
          {!collapsed && (
            <Link to="/" className="text-lg font-bold gradient-text">CareerAI</Link>
          )}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-white/5 rounded-lg"
          >
            <Bars3Icon className="w-5 h-5" />
          </button>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {NAV_ITEMS.map((item) => (
            <SidebarLink key={item.href} item={item} collapsed={collapsed} />
          ))}
        </nav>

        {/* User */}
        <div className="px-3 py-4 border-t border-white/5">
          {!collapsed && (
            <div className="mb-2 px-3">
              <p className="text-sm font-medium text-white truncate">{user?.full_name}</p>
              <p className="text-xs text-gray-500 truncate">{user?.email}</p>
            </div>
          )}
          <button
            onClick={logout}
            className={clsx(
              'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-gray-400 hover:text-white hover:bg-white/5 transition-colors',
            )}
          >
            <ArrowRightOnRectangleIcon className="w-5 h-5 shrink-0" />
            {!collapsed && <span>Sign Out</span>}
          </button>
        </div>
      </aside>

      {/* Mobile sidebar overlay */}
      {mobileOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="absolute inset-0 bg-black/60" onClick={() => setMobileOpen(false)} />
          <aside className="absolute left-0 top-0 h-full w-72 bg-gray-900 border-r border-white/5 flex flex-col z-50">
            <div className="flex items-center justify-between px-4 py-5 border-b border-white/5">
              <span className="text-lg font-bold gradient-text">CareerAI</span>
              <button onClick={() => setMobileOpen(false)} className="p-1.5 text-gray-400">
                <XMarkIcon className="w-5 h-5" />
              </button>
            </div>
            <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
              {NAV_ITEMS.map((item) => (
                <SidebarLink key={item.href} item={item} collapsed={false} onClick={() => setMobileOpen(false)} />
              ))}
            </nav>
            <div className="px-3 py-4 border-t border-white/5">
              <button
                onClick={() => { logout(); setMobileOpen(false) }}
                className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-gray-400 hover:text-white hover:bg-white/5"
              >
                <ArrowRightOnRectangleIcon className="w-5 h-5" />
                <span>Sign Out</span>
              </button>
            </div>
          </aside>
        </div>
      )}

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar */}
        <header className="h-14 border-b border-white/5 bg-gray-900/50 flex items-center px-4 gap-4 lg:hidden">
          <button onClick={() => setMobileOpen(true)} className="p-2 text-gray-400 hover:text-white">
            <Bars3Icon className="w-5 h-5" />
          </button>
          <span className="font-bold gradient-text">CareerAI</span>
        </header>

        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
