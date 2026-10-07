import { useState, useRef, useCallback, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import opportunitiesService from '../../services/opportunities.service'

// ── Constants ────────────────────────────────────────────────────────────────

const TABS = [
  { id: 'image', label: 'Screenshot / Image', icon: '🖼️' },
  { id: 'pdf', label: 'PDF', icon: '📄' },
  { id: 'url', label: 'URL', icon: '🔗' },
  { id: 'text', label: 'Paste Text', icon: '📝' },
]

const LOADING_STEPS = [
  'Extracting information…',
  'Verifying opportunity…',
  'Analyzing profile match…',
  'Saving results…',
]

const VERIFICATION_CONFIG = {
  genuine: {
    label: '✓ Appears Genuine',
    badge: 'bg-emerald-900/40 text-emerald-300 border-emerald-500/30',
    bar: 'bg-emerald-500',
  },
  could_not_verify: {
    label: '⚠ Could Not Fully Verify',
    badge: 'bg-amber-900/40 text-amber-300 border-amber-500/30',
    bar: 'bg-amber-500',
  },
  warning_signs: {
    label: '⚠ Warning Signs Detected',
    badge: 'bg-red-900/40 text-red-300 border-red-500/30',
    bar: 'bg-red-500',
  },
}

const APPLY_CONFIG = {
  apply_now: {
    label: 'APPLY NOW',
    color: 'bg-emerald-600 text-white',
    desc: 'Strong profile match — go for it!',
  },
  apply_upskill: {
    label: 'APPLY + UPSKILL',
    color: 'bg-blue-600 text-white',
    desc: 'Good match — apply while closing skill gaps.',
  },
  consider_after_upskill: {
    label: 'CONSIDER AFTER UPSKILLING',
    color: 'bg-amber-600 text-white',
    desc: 'Build key skills first, then apply.',
  },
  dont_prioritize: {
    label: "DON'T PRIORITIZE",
    color: 'bg-gray-600 text-white',
    desc: 'Significant skill gap — focus on other opportunities.',
  },
}

// ── Sub-components ────────────────────────────────────────────────────────────

function AnalyzingOverlay({ step }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-6">
      <div className="w-14 h-14 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      <p className="text-white font-medium">Checking opportunity…</p>
      <div className="space-y-2 w-72">
        {LOADING_STEPS.map((s, i) => (
          <div
            key={i}
            className={`flex items-center gap-2.5 text-sm transition-all duration-300 ${
              i < step ? 'text-gray-400' : i === step ? 'text-blue-300' : 'text-gray-600'
            }`}
          >
            {i < step ? (
              <svg className="w-4 h-4 text-emerald-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : i === step ? (
              <div className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin shrink-0" />
            ) : (
              <div className="w-4 h-4 rounded-full border border-gray-600 shrink-0" />
            )}
            {s}
          </div>
        ))}
      </div>
    </div>
  )
}

function InfoRow({ label, value }) {
  if (!value) return null
  return (
    <div className="flex flex-col sm:flex-row sm:gap-3">
      <span className="text-gray-500 text-xs uppercase tracking-wide w-32 shrink-0 pt-0.5">{label}</span>
      <span className="text-gray-200 text-sm break-words">{value}</span>
    </div>
  )
}

function SkillPill({ name, variant }) {
  const colors = {
    green: 'bg-emerald-900/40 text-emerald-300 border-emerald-500/30',
    orange: 'bg-orange-900/40 text-orange-300 border-orange-500/30',
  }
  return (
    <span className={`px-2.5 py-0.5 rounded-full border text-xs font-medium ${colors[variant]}`}>
      {name}
    </span>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────

export default function OpportunityChecker() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('text')
  const [textInput, setTextInput] = useState('')
  const [urlInput, setUrlInput] = useState('')
  const [imageFile, setImageFile] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [pdfFile, setPdfFile] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const [loading, setLoading] = useState(false)
  const [loadStep, setLoadStep] = useState(0)
  const [result, setResult] = useState(null)
  const fileInputRef = useRef(null)
  const pdfInputRef = useRef(null)
  const stepTimerRef = useRef(null)

  // Animate loading steps
  useEffect(() => {
    if (loading) {
      setLoadStep(0)
      stepTimerRef.current = setInterval(() => {
        setLoadStep((s) => Math.min(s + 1, LOADING_STEPS.length - 1))
      }, 900)
    } else {
      clearInterval(stepTimerRef.current)
    }
    return () => clearInterval(stepTimerRef.current)
  }, [loading])

  // Image drag-drop
  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setIsDragging(false)
    const dropped = e.dataTransfer.files[0]
    if (dropped && dropped.type.startsWith('image/')) {
      setImageFile(dropped)
      setImagePreview(URL.createObjectURL(dropped))
    } else {
      toast.error('Please drop an image file (JPG, PNG, or WebP)')
    }
  }, [])

  const handleImageSelect = (e) => {
    const f = e.target.files?.[0]
    if (f) {
      setImageFile(f)
      setImagePreview(URL.createObjectURL(f))
    }
  }

  const handlePdfSelect = (e) => {
    const f = e.target.files?.[0]
    if (f) setPdfFile(f)
  }

  const clearImage = () => {
    setImageFile(null)
    setImagePreview(null)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  const clearPdf = () => {
    setPdfFile(null)
    if (pdfInputRef.current) pdfInputRef.current.value = ''
  }

  const handleSubmit = async () => {
    setResult(null)

    let params = {}

    if (activeTab === 'text') {
      if (!textInput.trim()) { toast.error('Please paste the job description'); return }
      params = { inputType: 'text', text: textInput }
    } else if (activeTab === 'url') {
      if (!urlInput.trim()) { toast.error('Please enter a URL'); return }
      params = { inputType: 'url', url: urlInput }
    } else if (activeTab === 'image') {
      if (!imageFile) { toast.error('Please select or drop an image'); return }
      params = { inputType: 'screenshot', file: imageFile }
    } else if (activeTab === 'pdf') {
      if (!pdfFile) { toast.error('Please select a PDF file'); return }
      params = { inputType: 'pdf', file: pdfFile }
    }

    setLoading(true)
    try {
      const res = await opportunitiesService.check(params)
      setResult(res.data)
      toast.success('Opportunity checked!')
      // Scroll to results
      setTimeout(() => {
        document.getElementById('opp-results')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }, 200)
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to check opportunity'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  // ── Render helpers ────────────────────────────────────────────────────
  const ext = result?.extracted_data || {}
  const verStatus = result?.verification_status
  const verScore = result?.verification_score ?? 0
  const verDetails = result?.verification_details || {}
  const applyRec = result?.apply_recommendation
  const verCfg = verStatus ? VERIFICATION_CONFIG[verStatus] : null
  const applyCfg = applyRec ? APPLY_CONFIG[applyRec] : null
  const applyDetails = verDetails.apply_details || {}

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white mb-1">Opportunity Checker</h1>
        <p className="text-gray-400 text-sm">
          Paste, upload, or link a job posting to verify it and see how well it matches your profile.
        </p>
      </div>

      {/* Input Card */}
      <div className="rounded-2xl bg-gray-900 border border-white/10 overflow-hidden">
        {/* Tabs */}
        <div className="flex border-b border-white/10 overflow-x-auto">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-1.5 px-4 py-3 text-sm font-medium whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? 'text-blue-400 border-b-2 border-blue-500 bg-blue-500/5'
                  : 'text-gray-400 hover:text-gray-200'
              }`}
            >
              <span>{tab.icon}</span> {tab.label}
            </button>
          ))}
        </div>

        <div className="p-5">
          {/* Image / Screenshot tab */}
          {activeTab === 'image' && (
            <div className="space-y-3">
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/png,image/webp"
                className="hidden"
                onChange={handleImageSelect}
              />
              {imagePreview ? (
                <div className="relative rounded-xl overflow-hidden border border-white/10">
                  <img src={imagePreview} alt="Preview" className="w-full max-h-72 object-contain bg-black" />
                  <button
                    onClick={clearImage}
                    className="absolute top-2 right-2 w-7 h-7 rounded-full bg-black/70 text-white text-xs flex items-center justify-center hover:bg-black"
                  >
                    ✕
                  </button>
                </div>
              ) : (
                <div
                  onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
                  onDragLeave={() => setIsDragging(false)}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                  className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors ${
                    isDragging
                      ? 'border-blue-400 bg-blue-500/10'
                      : 'border-white/15 hover:border-white/30 hover:bg-white/5'
                  }`}
                >
                  <div className="text-4xl mb-3">🖼️</div>
                  <p className="text-gray-300 font-medium text-sm">Drag & drop a screenshot or click to browse</p>
                  <p className="text-gray-500 text-xs mt-1">JPG, PNG, WebP — max 10 MB</p>
                </div>
              )}
            </div>
          )}

          {/* PDF tab */}
          {activeTab === 'pdf' && (
            <div className="space-y-3">
              <input
                ref={pdfInputRef}
                type="file"
                accept="application/pdf,.pdf"
                className="hidden"
                onChange={handlePdfSelect}
              />
              {pdfFile ? (
                <div className="flex items-center gap-3 p-4 rounded-xl bg-gray-800 border border-white/10">
                  <span className="text-3xl">📄</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-white text-sm font-medium truncate">{pdfFile.name}</p>
                    <p className="text-gray-500 text-xs">{(pdfFile.size / 1024).toFixed(1)} KB</p>
                  </div>
                  <button
                    onClick={clearPdf}
                    className="text-gray-400 hover:text-white text-sm px-2 py-1 rounded hover:bg-white/10 transition"
                  >
                    Remove
                  </button>
                </div>
              ) : (
                <div
                  onClick={() => pdfInputRef.current?.click()}
                  className="border-2 border-dashed border-white/15 rounded-xl p-10 text-center cursor-pointer hover:border-white/30 hover:bg-white/5 transition-colors"
                >
                  <div className="text-4xl mb-3">📄</div>
                  <p className="text-gray-300 font-medium text-sm">Click to select a PDF job posting</p>
                  <p className="text-gray-500 text-xs mt-1">PDF only — max 10 MB</p>
                </div>
              )}
            </div>
          )}

          {/* URL tab */}
          {activeTab === 'url' && (
            <div className="space-y-2">
              <label className="text-gray-400 text-sm">Job posting URL</label>
              <input
                type="url"
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                placeholder="https://www.linkedin.com/jobs/view/..."
                className="w-full bg-gray-800 border border-white/15 rounded-xl px-4 py-3 text-white placeholder-gray-500 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition"
              />
              <p className="text-gray-600 text-xs">We'll fetch the page and extract the job details for you.</p>
            </div>
          )}

          {/* Text tab */}
          {activeTab === 'text' && (
            <div className="space-y-2">
              <label className="text-gray-400 text-sm">Paste job description</label>
              <textarea
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                rows={10}
                placeholder="Paste the full job description here…"
                className="w-full bg-gray-800 border border-white/15 rounded-xl px-4 py-3 text-white placeholder-gray-500 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition resize-none"
              />
            </div>
          )}

          {/* Submit */}
          <div className="mt-4 flex items-center justify-between gap-3">
            <p className="text-gray-600 text-xs max-w-xs">
              Results are automated checks only — always verify independently.
            </p>
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium rounded-xl text-sm transition-colors flex items-center gap-2"
            >
              {loading ? (
                <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : '🔍'}
              Check Opportunity
            </button>
          </div>
        </div>
      </div>

      {/* Loading state */}
      {loading && <AnalyzingOverlay step={loadStep} />}

      {/* Results */}
      {result && !loading && (
        <div id="opp-results" className="space-y-5">
          {/* ── Extracted Info Card ── */}
          <div className="rounded-2xl bg-gray-900 border border-white/10 p-5 space-y-4">
            <h2 className="text-white font-semibold text-base flex items-center gap-2">
              <span>📋</span> Extracted Information
            </h2>
            <div className="grid grid-cols-1 gap-2.5">
              <InfoRow label="Company" value={ext.company} />
              <InfoRow label="Role" value={ext.role} />
              <InfoRow label="Location" value={ext.location} />
              <InfoRow
                label="Salary"
                value={
                  ext.salary_min || ext.salary_max
                    ? `${ext.salary_currency === 'INR' ? '₹' : '$'}${
                        ext.salary_min ? (ext.salary_currency === 'INR' ? (ext.salary_min / 100_000).toFixed(1) + 'L' : ext.salary_min.toLocaleString()) : ''
                      }${ext.salary_max && ext.salary_max !== ext.salary_min
                        ? ` – ${ext.salary_currency === 'INR' ? (ext.salary_max / 100_000).toFixed(1) + 'L' : ext.salary_max.toLocaleString()}`
                        : ''} ${ext.salary_currency === 'INR' ? 'per annum' : 'USD'}`
                    : null
                }
              />
              <InfoRow label="Type" value={ext.job_type} />
              <InfoRow label="Experience" value={ext.experience_required} />
              <InfoRow label="Education" value={ext.education_required} />
              <InfoRow label="Deadline" value={ext.deadline} />
              <InfoRow label="Apply URL" value={ext.application_url} />
              <InfoRow label="Contact" value={ext.contact_email} />
            </div>
            {ext.skills_required?.length > 0 && (
              <div>
                <p className="text-gray-500 text-xs uppercase tracking-wide mb-2">Skills Required</p>
                <div className="flex flex-wrap gap-1.5">
                  {ext.skills_required.map((s) => (
                    <span key={s} className="px-2.5 py-0.5 rounded-full bg-gray-800 text-gray-300 text-xs border border-white/10">
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {!ext.company && !ext.role && (
              <p className="text-amber-400/80 text-sm">
                ⚠ Limited information was extracted. Try pasting the full text for better results.
              </p>
            )}
          </div>

          {/* ── Verification Card ── */}
          {verCfg && (
            <div className="rounded-2xl bg-gray-900 border border-white/10 p-5 space-y-4">
              <div className="flex items-start justify-between gap-4 flex-wrap">
                <h2 className="text-white font-semibold text-base flex items-center gap-2">
                  <span>🔎</span> Verification Result
                </h2>
                <span className={`px-3 py-1 rounded-full border text-sm font-semibold ${verCfg.badge}`}>
                  {verCfg.label}
                </span>
              </div>

              {/* Score bar */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-400">Verification Score</span>
                  <span className="text-white font-medium">{verScore}/100</span>
                </div>
                <div className="h-2 rounded-full bg-gray-800 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${verCfg.bar}`}
                    style={{ width: `${verScore}%` }}
                  />
                </div>
              </div>

              {/* Explanation */}
              <p className="text-gray-300 text-sm">{verDetails.explanation}</p>

              {/* Warning signs */}
              {verDetails.warning_signs?.length > 0 && (
                <div className="space-y-1.5">
                  <p className="text-red-400 text-xs font-semibold uppercase tracking-wide">Warning Signs</p>
                  {verDetails.warning_signs.map((w, i) => (
                    <div key={i} className="flex items-start gap-2 text-sm text-red-300/90">
                      <span className="shrink-0 mt-0.5">✗</span>
                      <span>{w}</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Positive signals */}
              {verDetails.positive_signals?.length > 0 && (
                <div className="space-y-1.5">
                  <p className="text-emerald-400 text-xs font-semibold uppercase tracking-wide">Positive Signals</p>
                  {verDetails.positive_signals.map((p, i) => (
                    <div key={i} className="flex items-start gap-2 text-sm text-emerald-300/90">
                      <span className="shrink-0 mt-0.5">✓</span>
                      <span>{p}</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Disclaimer */}
              <div className="flex items-start gap-2.5 px-3 py-2.5 rounded-xl bg-gray-800/50 border border-white/8 text-xs text-gray-500">
                <span className="shrink-0 text-yellow-500 mt-0.5">ℹ</span>
                {verDetails.disclaimer ||
                  'This is an automated check based on available signals. Always verify independently.'}
              </div>
            </div>
          )}

          {/* ── Apply Recommendation Card ── */}
          {applyCfg && (
            <div className="rounded-2xl bg-gray-900 border border-white/10 p-5 space-y-4">
              <h2 className="text-white font-semibold text-base flex items-center gap-2">
                <span>🎯</span> Apply Recommendation
              </h2>

              <div className="flex flex-col sm:flex-row sm:items-center gap-3">
                <span className={`px-4 py-2 rounded-xl font-bold text-sm tracking-wide ${applyCfg.color}`}>
                  {applyCfg.label}
                </span>
                <span className="text-gray-400 text-sm">{applyCfg.desc}</span>
              </div>

              <p className="text-gray-300 text-sm leading-relaxed">{result.apply_reasoning}</p>

              {/* Matched skills */}
              {applyDetails.matched_skills?.length > 0 && (
                <div>
                  <p className="text-gray-500 text-xs uppercase tracking-wide mb-2">Skills You Have ✓</p>
                  <div className="flex flex-wrap gap-1.5">
                    {applyDetails.matched_skills.map((s) => (
                      <SkillPill key={s} name={s} variant="green" />
                    ))}
                  </div>
                </div>
              )}

              {/* Missing skills */}
              {applyDetails.missing_skills?.length > 0 && (
                <div>
                  <p className="text-gray-500 text-xs uppercase tracking-wide mb-2">Skills to Learn</p>
                  <div className="flex flex-wrap gap-1.5">
                    {applyDetails.missing_skills.map((s) => (
                      <SkillPill key={s} name={s} variant="orange" />
                    ))}
                  </div>
                </div>
              )}

              {/* Upskill suggestions */}
              {applyDetails.upskill_suggestions?.length > 0 && (
                <div className="space-y-2">
                  <p className="text-gray-500 text-xs uppercase tracking-wide">Learning Resources</p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {applyDetails.upskill_suggestions.map((s, i) => (
                      <a
                        key={i}
                        href={s.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-start gap-2.5 p-3 rounded-xl bg-gray-800 border border-white/10 hover:border-blue-500/40 hover:bg-blue-500/5 transition-colors"
                      >
                        <span className="text-lg">📚</span>
                        <div className="min-w-0">
                          <p className="text-gray-300 text-xs font-medium truncate">{s.name}</p>
                          <p className="text-blue-400 text-xs mt-0.5 capitalize">{s.skill}</p>
                        </div>
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* History link */}
          <div className="flex justify-end gap-3">
            <button
              onClick={() => { setResult(null); setTextInput(''); setUrlInput(''); clearImage(); clearPdf() }}
              className="px-4 py-2 text-sm text-gray-400 hover:text-white border border-white/10 hover:border-white/25 rounded-xl transition-colors"
            >
              Check Another
            </button>
            <button
              onClick={() => navigate('/opportunity/history')}
              className="px-4 py-2 text-sm text-blue-400 hover:text-blue-300 border border-blue-500/30 hover:border-blue-400/50 rounded-xl transition-colors"
            >
              View History →
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
