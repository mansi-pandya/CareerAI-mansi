import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import JobsService from '../../services/jobs.service'
import Badge from '../../components/ui/Badge'

const STATUS_TABS = [
  { value: '', label: 'All Saved' },
  { value: 'applied', label: 'Applied' },
  { value: 'interested', label: 'Interested' },
  { value: 'ignored', label: 'Ignored' },
]

const STATUS_OPTIONS = [
  { value: 'saved', label: 'Saved' },
  { value: 'interested', label: 'Interested' },
  { value: 'applied', label: 'Applied' },
  { value: 'ignored', label: 'Ignored' },
]

const STATUS_COLORS = {
  saved: 'blue',
  interested: 'purple',
  applied: 'green',
  ignored: 'default',
}

const JOB_TYPE_LABELS = {
  internship: 'Internship',
  full_time: 'Full-time',
  part_time: 'Part-time',
  freelance: 'Freelance',
  contract: 'Contract',
  apprenticeship: 'Apprenticeship',
}

const WORK_MODE_LABELS = {
  remote: 'Remote',
  hybrid: 'Hybrid',
  on_site: 'On-site',
}

function formatSalary(min, max, currency) {
  if (!min && !max) return null
  const fmt = (n) => {
    if (currency === 'INR') {
      if (n >= 100000) return `₹${(n / 100000).toFixed(1)}L`
      return `₹${(n / 1000).toFixed(0)}K`
    }
    return `$${(n / 1000).toFixed(0)}K`
  }
  if (min && max) return `${fmt(min)} – ${fmt(max)}`
  if (min) return `${fmt(min)}+`
  return `Up to ${fmt(max)}`
}

function SavedJobCard({ job, onStatusChange, onRemove }) {
  const [editingNotes, setEditingNotes] = useState(false)
  const [notes, setNotes] = useState(job.saved_notes || '')
  const [saving, setSaving] = useState(false)

  const handleStatusChange = async (newStatus) => {
    setSaving(true)
    try {
      await JobsService.updateSavedStatus(job.id, newStatus)
      onStatusChange(job.id, newStatus)
      toast.success('Status updated')
    } catch {
      toast.error('Failed to update status')
    } finally {
      setSaving(false)
    }
  }

  const handleSaveNotes = async () => {
    setSaving(true)
    try {
      await JobsService.updateSavedStatus(job.id, job.saved_status, notes)
      onStatusChange(job.id, job.saved_status, notes)
      setEditingNotes(false)
      toast.success('Notes saved')
    } catch {
      toast.error('Failed to save notes')
    } finally {
      setSaving(false)
    }
  }

  const handleRemove = async () => {
    try {
      await JobsService.unsaveJob(job.id)
      onRemove(job.id)
      toast.success('Job removed from saved')
    } catch {
      toast.error('Failed to remove job')
    }
  }

  return (
    <div className="bg-gray-900 border border-white/6 rounded-xl p-5">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <Link
              to={`/jobs/${job.id}`}
              className="font-semibold text-white hover:text-blue-400 transition-colors"
            >
              {job.title}
            </Link>
            {job.is_demo && (
              <span className="text-[10px] text-yellow-500/70 border border-yellow-500/30 rounded px-1 py-0.5">
                Demo
              </span>
            )}
          </div>
          <p className="text-sm text-gray-400">{job.company}</p>
        </div>

        {/* Status badge + remove */}
        <div className="flex items-center gap-2 shrink-0">
          <Badge variant={STATUS_COLORS[job.saved_status] || 'default'}>
            {STATUS_OPTIONS.find((s) => s.value === job.saved_status)?.label || job.saved_status}
          </Badge>
          <button
            onClick={handleRemove}
            className="text-gray-600 hover:text-red-400 transition-colors p-1"
            title="Remove"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      {/* Meta */}
      <div className="flex flex-wrap items-center gap-2 mt-2">
        {job.location && (
          <span className="text-xs text-gray-500">{job.location}</span>
        )}
        {job.job_type && (
          <span className="text-xs text-gray-600">
            {JOB_TYPE_LABELS[job.job_type] || job.job_type}
          </span>
        )}
        {job.work_mode && (
          <span className="text-xs text-gray-600">
            {WORK_MODE_LABELS[job.work_mode] || job.work_mode}
          </span>
        )}
        {(job.salary_min || job.salary_max) && (
          <span className="text-xs text-emerald-400/80">
            {formatSalary(job.salary_min, job.salary_max, job.salary_currency)}
          </span>
        )}
      </div>

      {/* Skills */}
      {job.required_skills?.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-3">
          {job.required_skills.slice(0, 5).map((s) => (
            <span key={s} className="px-2 py-0.5 text-xs rounded-full bg-white/5 border border-white/10 text-gray-400">
              {s}
            </span>
          ))}
          {job.required_skills.length > 5 && (
            <span className="px-2 py-0.5 text-xs text-gray-600">
              +{job.required_skills.length - 5} more
            </span>
          )}
        </div>
      )}

      {/* Actions row */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 mt-4 pt-4 border-t border-white/5">
        {/* Status selector */}
        <select
          value={job.saved_status}
          onChange={(e) => handleStatusChange(e.target.value)}
          disabled={saving}
          className="bg-gray-800 border border-white/10 rounded-lg px-3 py-1.5 text-sm text-gray-300 focus:outline-none focus:border-blue-500/50 disabled:opacity-50"
        >
          {STATUS_OPTIONS.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </select>

        {/* Notes */}
        {editingNotes ? (
          <div className="flex-1 flex items-center gap-2">
            <input
              type="text"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Add a note…"
              className="flex-1 bg-gray-800 border border-white/10 rounded-lg px-3 py-1.5 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-blue-500/50"
              autoFocus
              onKeyDown={(e) => e.key === 'Enter' && handleSaveNotes()}
            />
            <button
              onClick={handleSaveNotes}
              disabled={saving}
              className="px-3 py-1.5 text-sm rounded-lg bg-blue-600 hover:bg-blue-500 text-white disabled:opacity-50 transition-colors"
            >
              Save
            </button>
            <button
              onClick={() => setEditingNotes(false)}
              className="px-3 py-1.5 text-sm rounded-lg border border-white/10 text-gray-400 hover:text-gray-200 transition-colors"
            >
              Cancel
            </button>
          </div>
        ) : (
          <button
            onClick={() => setEditingNotes(true)}
            className="text-xs text-gray-500 hover:text-gray-300 transition-colors flex items-center gap-1"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            {job.saved_notes ? 'Edit note' : 'Add note'}
          </button>
        )}

        {/* Apply */}
        {job.application_url && (
          <a
            href={job.application_url}
            target="_blank"
            rel="noopener noreferrer"
            className="ml-auto text-xs text-blue-400 hover:text-blue-300 transition-colors flex items-center gap-1"
          >
            Apply
            <svg className="w-3 h-3" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        )}
      </div>

      {/* Note display */}
      {!editingNotes && job.saved_notes && (
        <p className="mt-2 text-xs text-gray-500 italic">{job.saved_notes}</p>
      )}

      {/* Applied date */}
      {job.applied_at && (
        <p className="mt-1 text-[11px] text-gray-600">
          Applied:{' '}
          {new Date(job.applied_at).toLocaleDateString('en-IN', {
            day: 'numeric',
            month: 'short',
            year: 'numeric',
          })}
        </p>
      )}
    </div>
  )
}

export default function SavedJobs() {
  const [activeTab, setActiveTab] = useState('')
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)

  const loadJobs = async (status) => {
    setLoading(true)
    try {
      const data = await JobsService.getSavedJobs(status || null)
      setJobs(data)
    } catch {
      toast.error('Failed to load saved jobs')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadJobs(activeTab)
  }, [activeTab])

  const handleStatusChange = (jobId, newStatus, notes) => {
    setJobs((prev) =>
      prev.map((j) =>
        j.id === jobId
          ? { ...j, saved_status: newStatus, ...(notes !== undefined ? { saved_notes: notes } : {}) }
          : j,
      ),
    )
  }

  const handleRemove = (jobId) => {
    setJobs((prev) => prev.filter((j) => j.id !== jobId))
  }

  return (
    <div className="min-h-screen">
      {/* Header */}
      <div className="px-6 py-6 border-b border-white/6">
        <h1 className="text-2xl font-bold text-white mb-1">Saved Jobs</h1>
        <p className="text-sm text-gray-400">
          Track your applications and saved opportunities
        </p>
      </div>

      <div className="px-6 py-6">
        {/* Tabs */}
        <div className="flex items-center gap-1 mb-6 border-b border-white/6">
          {STATUS_TABS.map((tab) => (
            <button
              key={tab.value}
              onClick={() => setActiveTab(tab.value)}
              className={`px-4 py-2.5 text-sm font-medium transition-colors border-b-2 -mb-px ${
                activeTab === tab.value
                  ? 'text-white border-blue-500'
                  : 'text-gray-500 border-transparent hover:text-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="space-y-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-36 rounded-xl bg-gray-900 border border-white/6 animate-pulse" />
            ))}
          </div>
        ) : jobs.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <div className="w-14 h-14 rounded-2xl bg-gray-800 flex items-center justify-center mb-4 text-2xl">
              🔖
            </div>
            <p className="text-gray-300 font-medium mb-1">No saved jobs yet</p>
            <p className="text-sm text-gray-600 mb-5 max-w-xs">
              Browse jobs and click the bookmark icon to save listings you're interested in.
            </p>
            <Link
              to="/jobs"
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-sm font-medium hover:from-blue-500 hover:to-indigo-500 transition-all"
            >
              Browse Jobs
            </Link>
          </div>
        ) : (
          <div className="space-y-4 max-w-3xl">
            <p className="text-sm text-gray-600 mb-2">{jobs.length} job{jobs.length !== 1 ? 's' : ''}</p>
            {jobs.map((job) => (
              <SavedJobCard
                key={job.id}
                job={job}
                onStatusChange={handleStatusChange}
                onRemove={handleRemove}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
