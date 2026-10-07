import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import opportunitiesService from '../../services/opportunities.service'

// ── Config ─────────────────────────────────────────────────────────────────

const VERIFICATION_CONFIG = {
  genuine: {
    label: '✓ Genuine',
    badge: 'bg-emerald-900/40 text-emerald-300 border-emerald-500/30',
  },
  could_not_verify: {
    label: '⚠ Unverified',
    badge: 'bg-amber-900/40 text-amber-300 border-amber-500/30',
  },
  warning_signs: {
    label: '⚠ Warning Signs',
    badge: 'bg-red-900/40 text-red-300 border-red-500/30',
  },
}

const APPLY_CONFIG = {
  apply_now: { label: 'Apply Now', color: 'bg-emerald-600/20 text-emerald-300 border-emerald-500/30' },
  apply_upskill: { label: 'Apply + Upskill', color: 'bg-blue-600/20 text-blue-300 border-blue-500/30' },
  consider_after_upskill: { label: 'After Upskilling', color: 'bg-amber-600/20 text-amber-300 border-amber-500/30' },
  dont_prioritize: { label: "Don't Prioritize", color: 'bg-gray-700/50 text-gray-400 border-gray-600/30' },
}

const INPUT_ICONS = {
  text: '📝',
  url: '🔗',
  image: '🖼️',
  screenshot: '🖼️',
  pdf: '📄',
}

// ── Detail Drawer ──────────────────────────────────────────────────────────

function DetailDrawer({ check, onClose }) {
  if (!check) return null

  const ext = check.extracted_data || {}
  const verDetails = check.verification_details || {}
  const verCfg = check.verification_status ? VERIFICATION_CONFIG[check.verification_status] : null
  const applyCfg = check.apply_recommendation ? APPLY_CONFIG[check.apply_recommendation] : null
  const applyDetails = verDetails.apply_details || {}

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-2xl bg-gray-900 border border-white/15 shadow-2xl">
        {/* Header */}
        <div className="sticky top-0 bg-gray-900 border-b border-white/10 px-5 py-4 flex items-start justify-between gap-3">
          <div>
            <h2 className="text-white font-semibold text-base">
              {ext.role || 'Opportunity Detail'}
            </h2>
            <p className="text-gray-500 text-xs mt-0.5">
              {ext.company || 'Unknown company'} · {new Date(check.created_at).toLocaleDateString()}
            </p>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full border border-white/15 text-gray-400 hover:text-white flex items-center justify-center text-sm transition-colors"
          >
            ✕
          </button>
        </div>

        <div className="p-5 space-y-5">
          {/* Badges */}
          <div className="flex flex-wrap gap-2">
            {verCfg && (
              <span className={`px-3 py-1 rounded-full border text-xs font-semibold ${verCfg.badge}`}>
                {verCfg.label}
              </span>
            )}
            {applyCfg && (
              <span className={`px-3 py-1 rounded-full border text-xs font-semibold ${applyCfg.color}`}>
                {applyCfg.label}
              </span>
            )}
            {check.verification_score != null && (
              <span className="px-3 py-1 rounded-full border border-white/10 bg-gray-800 text-gray-300 text-xs">
                Score: {check.verification_score}/100
              </span>
            )}
          </div>

          {/* Extracted Info */}
          <div className="rounded-xl bg-gray-800/50 border border-white/8 p-4 space-y-2">
            <p className="text-gray-400 text-xs font-semibold uppercase tracking-wide mb-3">Extracted Info</p>
            {[
              ['Location', ext.location],
              ['Salary', ext.salary_min || ext.salary_max
                ? `${ext.salary_currency === 'INR' ? '₹' : '$'}${ext.salary_min ? (ext.salary_currency === 'INR' ? (ext.salary_min / 100_000).toFixed(1) + 'L' : ext.salary_min.toLocaleString()) : ''}${ext.salary_max && ext.salary_max !== ext.salary_min ? ` – ${ext.salary_currency === 'INR' ? (ext.salary_max / 100_000).toFixed(1) + 'L' : ext.salary_max.toLocaleString()}` : ''}`
                : null],
              ['Job Type', ext.job_type],
              ['Experience', ext.experience_required],
              ['Education', ext.education_required],
              ['Deadline', ext.deadline],
            ].filter(([, v]) => v).map(([label, value]) => (
              <div key={label} className="flex gap-2 text-sm">
                <span className="text-gray-500 w-24 shrink-0">{label}</span>
                <span className="text-gray-300">{value}</span>
              </div>
            ))}
            {ext.skills_required?.length > 0 && (
              <div className="flex gap-2 text-sm">
                <span className="text-gray-500 w-24 shrink-0">Skills</span>
                <div className="flex flex-wrap gap-1">
                  {ext.skills_required.map((s) => (
                    <span key={s} className="px-2 py-0.5 rounded-full bg-gray-700 text-gray-300 text-xs">{s}</span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Verification */}
          {verDetails.explanation && (
            <div className="space-y-3">
              <p className="text-gray-400 text-xs font-semibold uppercase tracking-wide">Verification</p>
              <p className="text-gray-300 text-sm">{verDetails.explanation}</p>
              {verDetails.warning_signs?.length > 0 && (
                <div className="space-y-1">
                  {verDetails.warning_signs.map((w, i) => (
                    <div key={i} className="flex items-start gap-2 text-sm text-red-300/90">
                      <span className="shrink-0">✗</span><span>{w}</span>
                    </div>
                  ))}
                </div>
              )}
              {verDetails.positive_signals?.length > 0 && (
                <div className="space-y-1">
                  {verDetails.positive_signals.map((p, i) => (
                    <div key={i} className="flex items-start gap-2 text-sm text-emerald-300/90">
                      <span className="shrink-0">✓</span><span>{p}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Apply Reasoning */}
          {check.apply_reasoning && (
            <div className="space-y-2">
              <p className="text-gray-400 text-xs font-semibold uppercase tracking-wide">Why This Recommendation</p>
              <p className="text-gray-300 text-sm leading-relaxed">{check.apply_reasoning}</p>
            </div>
          )}

          {/* Skills */}
          {applyDetails.matched_skills?.length > 0 && (
            <div>
              <p className="text-gray-500 text-xs uppercase tracking-wide mb-2">Skills You Have</p>
              <div className="flex flex-wrap gap-1.5">
                {applyDetails.matched_skills.map((s) => (
                  <span key={s} className="px-2.5 py-0.5 rounded-full bg-emerald-900/40 text-emerald-300 border border-emerald-500/30 text-xs">{s}</span>
                ))}
              </div>
            </div>
          )}
          {applyDetails.missing_skills?.length > 0 && (
            <div>
              <p className="text-gray-500 text-xs uppercase tracking-wide mb-2">Skills to Learn</p>
              <div className="flex flex-wrap gap-1.5">
                {applyDetails.missing_skills.map((s) => (
                  <span key={s} className="px-2.5 py-0.5 rounded-full bg-orange-900/40 text-orange-300 border border-orange-500/30 text-xs">{s}</span>
                ))}
              </div>
            </div>
          )}

          {/* Upskill links */}
          {applyDetails.upskill_suggestions?.length > 0 && (
            <div className="space-y-1.5">
              <p className="text-gray-500 text-xs uppercase tracking-wide">Learning Resources</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
                {applyDetails.upskill_suggestions.map((s, i) => (
                  <a
                    key={i}
                    href={s.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-800 hover:bg-gray-700/70 border border-white/8 text-xs text-blue-400 hover:text-blue-300 transition-colors"
                  >
                    📚 <span className="truncate">{s.name}</span>
                  </a>
                ))}
              </div>
            </div>
          )}

          {/* Disclaimer */}
          {verDetails.disclaimer && (
            <p className="text-gray-600 text-xs italic">{verDetails.disclaimer}</p>
          )}
        </div>
      </div>
    </div>
  )
}

// ── History Card ───────────────────────────────────────────────────────────

function HistoryCard({ check, onView, onDelete }) {
  const ext = check.extracted_data || {}
  const verCfg = check.verification_status ? VERIFICATION_CONFIG[check.verification_status] : null
  const applyCfg = check.apply_recommendation ? APPLY_CONFIG[check.apply_recommendation] : null
  const icon = INPUT_ICONS[check.input_type] || '📋'
  const [confirming, setConfirming] = useState(false)

  return (
    <div className="rounded-xl bg-gray-900 border border-white/10 p-4 hover:border-white/20 transition-colors group">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3 min-w-0">
          <span className="text-2xl shrink-0 mt-0.5">{icon}</span>
          <div className="min-w-0">
            <p className="text-white font-medium text-sm truncate">
              {ext.role || 'Unknown Role'}
            </p>
            <p className="text-gray-500 text-xs truncate">
              {ext.company || 'Unknown Company'} · {new Date(check.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1.5 shrink-0">
          <button
            onClick={() => onView(check)}
            className="px-3 py-1.5 text-xs text-blue-400 hover:text-blue-300 border border-blue-500/20 hover:border-blue-400/40 rounded-lg transition-colors"
          >
            View
          </button>
          {confirming ? (
            <>
              <button
                onClick={() => onDelete(check.id)}
                className="px-3 py-1.5 text-xs text-red-400 hover:text-red-300 border border-red-500/30 rounded-lg transition-colors"
              >
                Confirm
              </button>
              <button
                onClick={() => setConfirming(false)}
                className="px-3 py-1.5 text-xs text-gray-500 hover:text-gray-300 border border-white/10 rounded-lg transition-colors"
              >
                Cancel
              </button>
            </>
          ) : (
            <button
              onClick={() => setConfirming(true)}
              className="px-3 py-1.5 text-xs text-gray-500 hover:text-red-400 border border-white/10 hover:border-red-500/30 rounded-lg transition-colors"
            >
              Delete
            </button>
          )}
        </div>
      </div>

      {/* Badges */}
      <div className="flex flex-wrap gap-1.5 mt-3">
        {verCfg && (
          <span className={`px-2.5 py-0.5 rounded-full border text-xs font-medium ${verCfg.badge}`}>
            {verCfg.label}
          </span>
        )}
        {applyCfg && (
          <span className={`px-2.5 py-0.5 rounded-full border text-xs font-medium ${applyCfg.color}`}>
            {applyCfg.label}
          </span>
        )}
        {check.verification_score != null && (
          <span className="px-2.5 py-0.5 rounded-full bg-gray-800 text-gray-400 border border-white/8 text-xs">
            {check.verification_score}/100
          </span>
        )}
      </div>
    </div>
  )
}

// ── Main Page ──────────────────────────────────────────────────────────────

export default function OpportunityHistory() {
  const navigate = useNavigate()
  const [checks, setChecks] = useState([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState(null)

  const load = async () => {
    setLoading(true)
    try {
      const res = await opportunitiesService.history()
      setChecks(res.data || [])
    } catch {
      toast.error('Failed to load history')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleDelete = async (id) => {
    try {
      await opportunitiesService.delete(id)
      setChecks((prev) => prev.filter((c) => c.id !== id))
      if (selected?.id === id) setSelected(null)
      toast.success('Deleted')
    } catch {
      toast.error('Failed to delete')
    }
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">Opportunity History</h1>
          <p className="text-gray-400 text-sm">All your past opportunity checks.</p>
        </div>
        <button
          onClick={() => navigate('/opportunity')}
          className="px-4 py-2 text-sm bg-blue-600 hover:bg-blue-500 text-white rounded-xl transition-colors shrink-0"
        >
          + Check New
        </button>
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex justify-center py-16">
          <div className="w-10 h-10 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : checks.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <div className="text-5xl mb-4">🔍</div>
          <p className="text-white font-medium text-lg mb-2">No checks yet</p>
          <p className="text-gray-500 text-sm mb-6 max-w-xs">
            Verify your first opportunity to see results here.
          </p>
          <button
            onClick={() => navigate('/opportunity')}
            className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-xl transition-colors"
          >
            Check an Opportunity
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          <p className="text-gray-500 text-sm">{checks.length} check{checks.length !== 1 ? 's' : ''}</p>
          {checks.map((check) => (
            <HistoryCard
              key={check.id}
              check={check}
              onView={setSelected}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}

      {/* Detail Drawer */}
      {selected && (
        <DetailDrawer check={selected} onClose={() => setSelected(null)} />
      )}
    </div>
  )
}
