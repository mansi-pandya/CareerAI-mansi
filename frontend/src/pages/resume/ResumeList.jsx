import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import resumeService from '../../services/resume.service'

function ResumeCard({ resume, onDelete, onSetActive }) {
  const navigate = useNavigate()
  const [deleting, setDeleting] = useState(false)

  const handleDelete = async (e) => {
    e.stopPropagation()
    if (!window.confirm(`Delete "${resume.title}"? This cannot be undone.`)) return
    setDeleting(true)
    try {
      await resumeService.delete(resume.id)
      onDelete(resume.id)
      toast.success('Resume deleted')
    } catch {
      toast.error('Failed to delete resume')
    } finally {
      setDeleting(false)
    }
  }

  const handleSetActive = async (e) => {
    e.stopPropagation()
    try {
      await resumeService.setActive(resume.id)
      onSetActive(resume.id)
      toast.success(`"${resume.title}" set as active resume`)
    } catch {
      toast.error('Failed to set active resume')
    }
  }

  const fmtDate = (d) =>
    new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })

  return (
    <div
      onClick={() => navigate(`/resume/${resume.id}`)}
      className={`relative p-5 rounded-xl border cursor-pointer transition-all hover:border-blue-500/50 hover:bg-white/5 ${
        resume.is_active
          ? 'border-emerald-500/50 bg-emerald-900/10'
          : 'border-white/10 bg-white/3'
      }`}
    >
      {resume.is_active && (
        <span className="absolute top-3 right-3 text-xs font-medium px-2 py-0.5 rounded-full bg-emerald-900/50 text-emerald-400 border border-emerald-500/30">
          Active
        </span>
      )}
      <div className="flex items-start gap-4">
        <div className="w-10 h-12 rounded-lg bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center flex-shrink-0 mt-0.5">
          <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-white font-semibold truncate pr-16">{resume.title}</h3>
          <p className="text-gray-500 text-sm mt-0.5">Updated {fmtDate(resume.updated_at)}</p>
        </div>
      </div>
      <div className="flex gap-2 mt-4" onClick={(e) => e.stopPropagation()}>
        <button
          onClick={() => navigate(`/resume/${resume.id}/builder`)}
          className="flex-1 text-xs py-1.5 rounded-lg bg-white/8 hover:bg-white/12 text-gray-300 transition-colors"
        >
          Edit
        </button>
        <button
          onClick={() => navigate(`/resume/${resume.id}/preview`)}
          className="flex-1 text-xs py-1.5 rounded-lg bg-white/8 hover:bg-white/12 text-gray-300 transition-colors"
        >
          Preview
        </button>
        {!resume.is_active && (
          <button
            onClick={handleSetActive}
            className="flex-1 text-xs py-1.5 rounded-lg bg-blue-900/40 hover:bg-blue-900/60 text-blue-300 transition-colors"
          >
            Set Active
          </button>
        )}
        <button
          onClick={handleDelete}
          disabled={deleting}
          className="px-3 py-1.5 rounded-lg bg-red-900/30 hover:bg-red-900/50 text-red-400 text-xs transition-colors disabled:opacity-50"
        >
          {deleting ? '…' : 'Delete'}
        </button>
      </div>
    </div>
  )
}

export default function ResumeList() {
  const navigate = useNavigate()
  const [resumes, setResumes] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    resumeService.list()
      .then((r) => setResumes(r.data))
      .catch(() => toast.error('Failed to load resumes'))
      .finally(() => setLoading(false))
  }, [])

  const handleDelete = (id) => setResumes((prev) => prev.filter((r) => r.id !== id))
  const handleSetActive = (id) =>
    setResumes((prev) =>
      prev.map((r) => ({ ...r, is_active: r.id === id }))
    )

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white">My Resumes</h1>
          <p className="text-gray-400 text-sm mt-1">Manage, edit, and analyze your resumes</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => navigate('/resume/upload')}
            className="flex items-center gap-2 px-4 py-2 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 text-gray-300 text-sm transition-all"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
            Upload
          </button>
          <button
            onClick={() => navigate('/resume/create')}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-sm font-medium transition-all"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Build New
          </button>
        </div>
      </div>

      {/* Empty state */}
      {resumes.length === 0 ? (
        <div className="text-center py-20 rounded-2xl border border-dashed border-white/10 bg-white/3">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-600/20 to-indigo-700/20 border border-white/10 flex items-center justify-center mx-auto mb-4">
            <svg className="w-7 h-7 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="text-gray-300 font-semibold mb-2">No resumes yet</h3>
          <p className="text-gray-500 text-sm mb-6">Upload an existing resume or build one from scratch.</p>
          <div className="flex gap-3 justify-center">
            <button
              onClick={() => navigate('/resume/upload')}
              className="px-4 py-2 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 text-gray-300 text-sm"
            >
              Upload Resume
            </button>
            <button
              onClick={() => navigate('/resume/create')}
              className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium"
            >
              Build from Scratch
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {resumes.map((resume) => (
            <ResumeCard
              key={resume.id}
              resume={resume}
              onDelete={handleDelete}
              onSetActive={handleSetActive}
            />
          ))}
        </div>
      )}
    </div>
  )
}
