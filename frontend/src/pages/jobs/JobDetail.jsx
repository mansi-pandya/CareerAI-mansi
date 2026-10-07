import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import JobsService from '../../services/jobs.service'
import JobMatchBreakdown from '../../components/jobs/JobMatchBreakdown'
import JobCard from '../../components/jobs/JobCard'
import Badge from '../../components/ui/Badge'

const JOB_TYPE_COLORS = {
  internship: 'purple',
  full_time: 'green',
  part_time: 'blue',
  freelance: 'orange',
  contract: 'yellow',
  apprenticeship: 'teal',
}

const WORK_MODE_COLORS = {
  remote: 'green',
  hybrid: 'blue',
  on_site: 'default',
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
  const sym = currency === 'INR' ? '₹' : '$'
  const fmt = (n) => {
    if (currency === 'INR') {
      if (n >= 100000) return `₹${(n / 100000).toFixed(1)}L`
      return `₹${(n / 1000).toFixed(0)}K`
    }
    return `$${(n / 1000).toFixed(0)}K`
  }
  if (min && max) return `${fmt(min)} – ${fmt(max)} / year`
  if (min) return `${fmt(min)}+ / year`
  return `Up to ${fmt(max)} / year`
}

function formatDate(dateStr) {
  if (!dateStr) return null
  return new Date(dateStr).toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

export default function JobDetail() {
  const { jobId } = useParams()
  const navigate = useNavigate()
  const [job, setJob] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    let cancelled = false
    const load = async () => {
      setLoading(true)
      try {
        const data = await JobsService.getJob(jobId)
        if (!cancelled) setJob(data)
      } catch {
        toast.error('Job not found')
        if (!cancelled) navigate('/jobs')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => { cancelled = true }
  }, [jobId]) // eslint-disable-line

  const handleSave = async () => {
    setSaving(true)
    try {
      if (job.is_saved) {
        await JobsService.unsaveJob(job.id)
        setJob((prev) => ({ ...prev, is_saved: false }))
        toast.success('Removed from saved')
      } else {
        await JobsService.saveJob(job.id)
        setJob((prev) => ({ ...prev, is_saved: true }))
        toast.success('Job saved!')
      }
    } catch {
      toast.error('Failed to update saved status')
    } finally {
      setSaving(false)
    }
  }

  const handleSaveSimilar = async (id) => {
    try {
      await JobsService.saveJob(id)
      toast.success('Job saved!')
    } catch {
      toast.error('Failed to save job')
    }
  }

  if (loading) {
    return (
      <div className="p-6 space-y-4">
        <div className="h-8 w-1/3 rounded-lg bg-gray-800 animate-pulse" />
        <div className="h-4 w-1/2 rounded-lg bg-gray-800 animate-pulse" />
        <div className="h-64 rounded-xl bg-gray-800 animate-pulse" />
      </div>
    )
  }

  if (!job) return null

  const hasMatch = job.overall_score != null
  const matchObj = hasMatch
    ? {
        overall_score: job.overall_score,
        skill_score: job.skill_score,
        role_score: job.role_score,
        education_score: job.education_score,
        experience_score: job.experience_score,
        location_score: job.location_score,
        preference_score: job.preference_score,
        match_reasons: job.match_reasons || [],
      }
    : null

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6">
      {/* Back link */}
      <Link
        to="/jobs"
        className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-300 mb-5 transition-colors"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
        Back to Jobs
      </Link>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main content */}
        <div className="lg:col-span-2 space-y-5">
          {/* Header card */}
          <div className="bg-gray-900 border border-white/6 rounded-xl p-6">
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 flex-wrap mb-1">
                  <h1 className="text-xl font-bold text-white">{job.title}</h1>
                  {job.is_demo && (
                    <span className="text-[11px] text-yellow-500/70 border border-yellow-500/30 rounded px-1.5 py-0.5">
                      Demo
                    </span>
                  )}
                </div>
                <p className="text-gray-400 text-base">{job.company}</p>
              </div>
              {/* Save + Apply */}
              <div className="flex items-center gap-2 shrink-0">
                <button
                  onClick={handleSave}
                  disabled={saving}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg border text-sm font-medium transition-colors ${
                    job.is_saved
                      ? 'bg-blue-900/30 border-blue-500/40 text-blue-300 hover:bg-blue-900/50'
                      : 'border-white/15 text-gray-300 hover:bg-white/5'
                  }`}
                >
                  <svg className="w-4 h-4" fill={job.is_saved ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M17 3H7a2 2 0 00-2 2v16l7-3 7 3V5a2 2 0 00-2-2z" />
                  </svg>
                  {job.is_saved ? 'Saved' : 'Save'}
                </button>
                {job.application_url && (
                  <a
                    href={job.application_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-sm font-medium transition-all"
                  >
                    Apply
                    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                )}
              </div>
            </div>

            {/* Meta row */}
            <div className="flex flex-wrap items-center gap-3 mt-4">
              {job.location && (
                <span className="flex items-center gap-1 text-sm text-gray-400">
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  {job.location}
                </span>
              )}
              {job.job_type && (
                <Badge variant={JOB_TYPE_COLORS[job.job_type] || 'default'}>
                  {JOB_TYPE_LABELS[job.job_type] || job.job_type}
                </Badge>
              )}
              {job.work_mode && (
                <Badge variant={WORK_MODE_COLORS[job.work_mode] || 'default'}>
                  {WORK_MODE_LABELS[job.work_mode] || job.work_mode}
                </Badge>
              )}
              {job.source_name && (
                <span className="text-xs text-gray-600">via {job.source_name}</span>
              )}
            </div>

            {/* Salary & Experience */}
            <div className="flex flex-wrap gap-4 mt-4">
              {(job.salary_min || job.salary_max) && (
                <div className="flex items-center gap-1.5 text-sm text-emerald-400">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {formatSalary(job.salary_min, job.salary_max, job.salary_currency)}
                </div>
              )}
              {(job.experience_min_years != null || job.experience_max_years != null) && (
                <div className="flex items-center gap-1.5 text-sm text-gray-400">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  {job.experience_min_years === 0
                    ? 'Fresher / No experience required'
                    : `${job.experience_min_years}${job.experience_max_years ? `–${job.experience_max_years}` : '+'} yrs experience`}
                </div>
              )}
              {job.posted_date && (
                <div className="text-xs text-gray-600">
                  Posted {formatDate(job.posted_date)}
                </div>
              )}
            </div>
          </div>

          {/* Required Skills */}
          {job.required_skills?.length > 0 && (
            <div className="bg-gray-900 border border-white/6 rounded-xl p-5">
              <h2 className="text-sm font-semibold text-gray-200 mb-3">Required Skills</h2>
              <div className="flex flex-wrap gap-2">
                {job.required_skills.map((skill) => {
                  const matched = job.match_reasons?.some((r) =>
                    r.toLowerCase().includes(skill.toLowerCase()),
                  )
                  return (
                    <span
                      key={skill}
                      className={`px-3 py-1 text-sm rounded-full border ${
                        matched
                          ? 'bg-emerald-900/30 border-emerald-500/40 text-emerald-300'
                          : 'bg-white/4 border-white/10 text-gray-300'
                      }`}
                    >
                      {skill}
                      {matched && (
                        <span className="ml-1.5 text-emerald-400 text-xs">✓</span>
                      )}
                    </span>
                  )
                })}
              </div>
            </div>
          )}

          {/* Description */}
          {job.description && (
            <div className="bg-gray-900 border border-white/6 rounded-xl p-5">
              <h2 className="text-sm font-semibold text-gray-200 mb-3">Job Description</h2>
              <div className="text-sm text-gray-300 leading-relaxed whitespace-pre-line">
                {job.description}
              </div>
            </div>
          )}

          {/* Similar jobs */}
          {job.similar_jobs?.length > 0 && (
            <div>
              <h2 className="text-sm font-semibold text-gray-200 mb-3">Similar Jobs</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {job.similar_jobs.map((sj) => (
                  <JobCard key={sj.id} job={sj} onSave={handleSaveSimilar} compact />
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Sidebar — match breakdown */}
        <div className="space-y-5">
          {matchObj ? (
            <div className="bg-gray-900 border border-white/6 rounded-xl p-5">
              <h2 className="text-sm font-semibold text-gray-200 mb-4">Your Match</h2>
              <JobMatchBreakdown match={matchObj} />
            </div>
          ) : (
            <div className="bg-gray-900 border border-white/6 rounded-xl p-5 text-center">
              <p className="text-sm text-gray-500 mb-3">
                Log in to see your personalized match score for this job.
              </p>
              <Link
                to="/login"
                className="inline-block px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium transition-colors"
              >
                Log In
              </Link>
            </div>
          )}

          {/* Apply CTA */}
          {job.application_url && (
            <a
              href={job.application_url}
              target="_blank"
              rel="noopener noreferrer"
              className="block w-full text-center px-4 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-sm transition-all"
            >
              Apply for this Job →
            </a>
          )}
        </div>
      </div>
    </div>
  )
}
