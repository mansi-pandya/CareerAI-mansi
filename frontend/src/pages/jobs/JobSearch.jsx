import { useState, useEffect, useCallback, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import JobsService from '../../services/jobs.service'
import JobCard from '../../components/jobs/JobCard'
import JobFilters from '../../components/jobs/JobFilters'

const SORT_OPTIONS = [
  { value: 'match', label: 'Best Match' },
  { value: 'newest', label: 'Newest' },
  { value: 'salary', label: 'Highest Salary' },
]

function DemoBanner() {
  return (
    <div className="flex items-start gap-3 px-4 py-3 rounded-xl bg-yellow-900/20 border border-yellow-500/25 text-yellow-300/90 text-sm">
      <span className="text-yellow-400 shrink-0 mt-0.5">ℹ</span>
      <span>
        Some results are demo jobs for illustration purposes.{' '}
        <span className="text-yellow-400/70">
          Configure Adzuna API keys in your environment to see real job listings.
        </span>
      </span>
    </div>
  )
}

function Pagination({ page, total, limit, onChange }) {
  const totalPages = Math.ceil(total / limit)
  if (totalPages <= 1) return null

  return (
    <div className="flex items-center justify-center gap-2 pt-6">
      <button
        disabled={page <= 1}
        onClick={() => onChange(page - 1)}
        className="px-3 py-1.5 text-sm rounded-lg border border-white/10 text-gray-300 disabled:opacity-30 hover:bg-white/5 transition-colors"
      >
        ← Prev
      </button>
      <span className="text-sm text-gray-500 px-2">
        Page {page} of {totalPages}
      </span>
      <button
        disabled={page >= totalPages}
        onClick={() => onChange(page + 1)}
        className="px-3 py-1.5 text-sm rounded-lg border border-white/10 text-gray-300 disabled:opacity-30 hover:bg-white/5 transition-colors"
      >
        Next →
      </button>
    </div>
  )
}

const DEFAULT_FILTERS = {
  jobTypes: [],
  workModes: [],
  location: '',
  salaryMin: '',
  salaryMax: '',
  experienceMin: '',
  skills: [],
  source: '',
}

export default function JobSearch() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [keywords, setKeywords] = useState(searchParams.get('q') || '')
  const [filters, setFilters] = useState(DEFAULT_FILTERS)
  const [sortBy, setSortBy] = useState('match')
  const [page, setPage] = useState(1)
  const [jobs, setJobs] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [hasDemo, setHasDemo] = useState(false)
  const [filtersOpen, setFiltersOpen] = useState(false)
  const debounceRef = useRef(null)

  const fetchJobs = useCallback(
    async (kw, f, sort, pg) => {
      setLoading(true)
      try {
        const params = {
          keywords: kw || undefined,
          page: pg,
          limit: 20,
          sortBy: sort,
        }
        if (f.jobTypes.length === 1) params.jobType = f.jobTypes[0]
        if (f.workModes.length === 1) params.workMode = f.workModes[0]
        if (f.location) params.location = f.location
        if (f.salaryMin) params.salaryMin = parseInt(f.salaryMin)
        if (f.salaryMax) params.salaryMax = parseInt(f.salaryMax)
        if (f.skills.length) params.skills = f.skills
        if (f.source) params.source = f.source

        const data = await JobsService.searchJobs(params)
        setJobs(data.jobs || [])
        setTotal(data.total || 0)
        setHasDemo(data.has_demo || false)
      } catch (err) {
        console.error(err)
        toast.error('Failed to load jobs')
      } finally {
        setLoading(false)
      }
    },
    [],
  )

  // Debounced keyword search
  useEffect(() => {
    clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => {
      setPage(1)
      fetchJobs(keywords, filters, sortBy, 1)
    }, 400)
    return () => clearTimeout(debounceRef.current)
  }, [keywords, filters, sortBy]) // eslint-disable-line

  useEffect(() => {
    fetchJobs(keywords, filters, sortBy, page)
  }, [page]) // eslint-disable-line

  const handleSave = async (jobId) => {
    try {
      await JobsService.saveJob(jobId)
      setJobs((prev) => prev.map((j) => (j.id === jobId ? { ...j, is_saved: true } : j)))
      toast.success('Job saved!')
    } catch {
      toast.error('Failed to save job')
    }
  }

  const handleUnsave = async (jobId) => {
    try {
      await JobsService.unsaveJob(jobId)
      setJobs((prev) => prev.map((j) => (j.id === jobId ? { ...j, is_saved: false } : j)))
      toast.success('Job removed from saved')
    } catch {
      toast.error('Failed to unsave job')
    }
  }

  const handleRefresh = async () => {
    try {
      setLoading(true)
      await JobsService.refreshJobs(keywords || 'software developer', filters.location || 'India')
      toast.success('Jobs refreshed!')
      fetchJobs(keywords, filters, sortBy, 1)
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Please wait 1 minute between refreshes'
      toast.error(msg)
      setLoading(false)
    }
  }

  const activeFilterCount =
    filters.jobTypes.length +
    filters.workModes.length +
    (filters.location ? 1 : 0) +
    (filters.salaryMin || filters.salaryMax ? 1 : 0) +
    filters.skills.length +
    (filters.source ? 1 : 0)

  return (
    <div className="min-h-screen">
      {/* Page header */}
      <div className="px-6 py-6 border-b border-white/6">
        <h1 className="text-2xl font-bold text-white mb-1">Job Discovery</h1>
        <p className="text-sm text-gray-400">
          Find internships and jobs matched to your profile
        </p>
      </div>

      <div className="px-6 py-6">
        {/* Search + controls row */}
        <div className="flex flex-col sm:flex-row gap-3 mb-6">
          {/* Search bar */}
          <div className="relative flex-1">
            <svg
              className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500"
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
              viewBox="0 0 24 24"
            >
              <circle cx={11} cy={11} r={8} />
              <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-4.35-4.35" />
            </svg>
            <input
              type="text"
              value={keywords}
              onChange={(e) => {
                setKeywords(e.target.value)
                setSearchParams(e.target.value ? { q: e.target.value } : {})
              }}
              placeholder="Search by title, company, or skill…"
              className="w-full bg-gray-900 border border-white/10 rounded-xl pl-10 pr-4 py-2.5 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-blue-500/50"
            />
          </div>

          {/* Sort */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="bg-gray-900 border border-white/10 rounded-xl px-3 py-2.5 text-sm text-gray-200 focus:outline-none focus:border-blue-500/50"
          >
            {SORT_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>

          {/* Filter toggle (mobile) */}
          <button
            onClick={() => setFiltersOpen(!filtersOpen)}
            className="sm:hidden flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gray-800 border border-white/10 text-sm text-gray-300"
          >
            Filters {activeFilterCount > 0 && `(${activeFilterCount})`}
          </button>

          {/* Refresh */}
          <button
            onClick={handleRefresh}
            disabled={loading}
            title="Refresh job listings"
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gray-800 border border-white/10 text-sm text-gray-300 hover:bg-gray-700 disabled:opacity-50 transition-colors"
          >
            <svg className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span className="hidden sm:inline">Refresh</span>
          </button>
        </div>

        {/* Demo banner */}
        {hasDemo && <div className="mb-5"><DemoBanner /></div>}

        <div className="flex gap-6">
          {/* Sidebar filters — desktop */}
          <aside className="hidden sm:block w-60 shrink-0">
            <div className="bg-gray-900 border border-white/6 rounded-xl p-5">
              <p className="text-sm font-semibold text-gray-200 mb-4">
                Filters
                {activeFilterCount > 0 && (
                  <span className="ml-2 text-xs text-blue-400">({activeFilterCount})</span>
                )}
              </p>
              <JobFilters filters={filters} onChange={setFilters} />
            </div>
          </aside>

          {/* Mobile filters panel */}
          {filtersOpen && (
            <div className="fixed inset-0 z-50 bg-gray-950/90 sm:hidden overflow-y-auto p-6">
              <div className="bg-gray-900 border border-white/10 rounded-xl p-5">
                <div className="flex items-center justify-between mb-4">
                  <p className="font-semibold text-white">Filters</p>
                  <button onClick={() => setFiltersOpen(false)} className="text-gray-400 hover:text-white">
                    ✕
                  </button>
                </div>
                <JobFilters filters={filters} onChange={setFilters} />
                <button
                  onClick={() => setFiltersOpen(false)}
                  className="mt-5 w-full py-2.5 rounded-xl bg-blue-600 text-white text-sm font-medium"
                >
                  Apply Filters
                </button>
              </div>
            </div>
          )}

          {/* Results */}
          <div className="flex-1 min-w-0">
            {/* Result count */}
            <div className="flex items-center justify-between mb-4">
              <p className="text-sm text-gray-500">
                {loading ? 'Loading…' : `${total.toLocaleString()} job${total !== 1 ? 's' : ''} found`}
              </p>
            </div>

            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Array.from({ length: 6 }).map((_, i) => (
                  <div key={i} className="h-48 rounded-xl bg-gray-900 border border-white/6 animate-pulse" />
                ))}
              </div>
            ) : jobs.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-20 text-center">
                <div className="w-14 h-14 rounded-2xl bg-gray-800 flex items-center justify-center mb-4 text-2xl">
                  🔍
                </div>
                <p className="text-gray-300 font-medium mb-1">No jobs found</p>
                <p className="text-sm text-gray-600 max-w-xs">
                  Try different keywords or filters, or click Refresh to load more listings.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {jobs.map((job) => (
                  <JobCard
                    key={job.id}
                    job={job}
                    onSave={handleSave}
                    onUnsave={handleUnsave}
                  />
                ))}
              </div>
            )}

            <Pagination page={page} total={total} limit={20} onChange={setPage} />
          </div>
        </div>
      </div>
    </div>
  )
}
