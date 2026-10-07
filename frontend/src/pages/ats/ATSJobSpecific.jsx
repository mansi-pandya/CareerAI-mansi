import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import resumeService from '../../services/resume.service'
import atsService from '../../services/ats.service'
import ScoreCircle from '../../components/ui/ScoreCircle'
import ATSRecommendationCard from '../../components/resume/ATSRecommendationCard'

function KeywordChip({ word, matched }) {
  return (
    <span
      className={`px-2.5 py-1 rounded-lg text-xs font-medium border ${
        matched
          ? 'bg-emerald-900/30 text-emerald-300 border-emerald-500/20'
          : 'bg-red-900/30 text-red-300 border-red-500/20'
      }`}
    >
      {matched ? '✓ ' : '✗ '}{word}
    </span>
  )
}

export default function ATSJobSpecific() {
  const [searchParams] = useSearchParams()
  const [resumes, setResumes] = useState([])
  const [selectedResume, setSelectedResume] = useState(searchParams.get('resume') || '')
  const [jobDescription, setJobDescription] = useState('')
  const [analyzing, setAnalyzing] = useState(false)
  const [result, setResult] = useState(null)

  useEffect(() => {
    resumeService.list()
      .then((r) => {
        setResumes(r.data)
        if (!selectedResume && r.data.length > 0) {
          const active = r.data.find((x) => x.is_active)
          setSelectedResume(String(active?.id || r.data[0].id))
        }
      })
      .catch(() => {})
  }, [])

  const handleAnalyze = async () => {
    if (!selectedResume) { toast.error('Select a resume first'); return }
    if (!jobDescription.trim()) { toast.error('Paste a job description first'); return }
    setAnalyzing(true)
    setResult(null)
    try {
      const { data } = await atsService.analyzeWithJob(selectedResume, jobDescription)
      setResult(data)
      toast.success('Job-specific analysis complete!')
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Analysis failed')
    } finally {
      setAnalyzing(false)
    }
  }

  const matchedKw = result?.analysis_data?.job_alignment?.matched_keywords || []
  const missingKw = result?.analysis_data?.job_alignment?.missing_keywords || []
  const jobAlignmentScore = result?.job_alignment_score || 0

  const getMatchStatus = () => {
    if (jobAlignmentScore >= 75) return { label: 'Strong Match', color: 'text-emerald-400' }
    if (jobAlignmentScore >= 50) return { label: 'Moderate Match', color: 'text-amber-400' }
    return { label: 'Weak Match', color: 'text-red-400' }
  }
  const matchStatus = getMatchStatus()

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Job-Specific ATS Check</h1>
        <p className="text-gray-400 text-sm mt-1">Paste a job description and see how well your resume matches it</p>
      </div>

      {/* Inputs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Resume select */}
        <div className="p-4 rounded-xl bg-white/3 border border-white/8 space-y-3">
          <h3 className="text-white font-medium text-sm">Your Resume</h3>
          <select
            value={selectedResume}
            onChange={(e) => setSelectedResume(e.target.value)}
            className="w-full bg-gray-800 border border-white/10 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-blue-500"
          >
            <option value="">-- Select resume --</option>
            {resumes.map((r) => (
              <option key={r.id} value={r.id}>{r.title}{r.is_active ? ' (Active)' : ''}</option>
            ))}
          </select>
        </div>

        {/* Job description */}
        <div className="p-4 rounded-xl bg-white/3 border border-white/8 space-y-3">
          <h3 className="text-white font-medium text-sm">Job Description</h3>
          <textarea
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            rows={5}
            placeholder="Paste the job description here…"
            className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-blue-500 resize-none"
          />
          <p className="text-gray-600 text-xs">{jobDescription.trim().split(/\s+/).filter(Boolean).length} words</p>
        </div>
      </div>

      <button
        onClick={handleAnalyze}
        disabled={analyzing || !selectedResume || !jobDescription.trim()}
        className="w-full py-3 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-medium disabled:opacity-40 disabled:cursor-not-allowed transition-all"
      >
        {analyzing ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Analyzing…
          </span>
        ) : 'Analyze Match'}
      </button>

      {/* Results */}
      {result && (
        <div className="space-y-5">
          {/* Match overview */}
          <div className="flex flex-col sm:flex-row items-center gap-6 p-6 rounded-2xl bg-gradient-to-br from-gray-800/80 to-gray-900/80 border border-white/10">
            <ScoreCircle score={jobAlignmentScore} size={120} strokeWidth={9} label="Job Alignment" />
            <div>
              <p className={`text-3xl font-bold ${matchStatus.color}`}>{matchStatus.label}</p>
              <p className="text-gray-400 text-sm mt-1">
                Your resume matches {matchedKw.length} of the detected job keywords
              </p>
              <p className="text-gray-500 text-xs mt-2">
                Overall ATS score: <span className="text-gray-300">{Math.round(result.overall_score)}/100</span>
              </p>
            </div>
          </div>

          {/* Keyword comparison */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            {/* Matched keywords */}
            <div className="p-5 rounded-xl bg-emerald-900/10 border border-emerald-500/20">
              <div className="flex items-center gap-2 mb-3">
                <svg className="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <h3 className="text-emerald-400 font-medium text-sm">Matching Keywords ({matchedKw.length})</h3>
              </div>
              {matchedKw.length === 0 ? (
                <p className="text-gray-500 text-xs">No matching keywords found</p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {matchedKw.map((kw, i) => <KeywordChip key={i} word={kw} matched={true} />)}
                </div>
              )}
            </div>

            {/* Missing keywords */}
            <div className="p-5 rounded-xl bg-red-900/10 border border-red-500/20">
              <div className="flex items-center gap-2 mb-3">
                <svg className="w-4 h-4 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                <h3 className="text-red-400 font-medium text-sm">Missing Keywords ({missingKw.length})</h3>
              </div>
              {missingKw.length === 0 ? (
                <p className="text-gray-500 text-xs">No major missing keywords — great match!</p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {missingKw.map((kw, i) => <KeywordChip key={i} word={kw} matched={false} />)}
                </div>
              )}
            </div>
          </div>

          {/* Skill alignment sub-score */}
          <div className="p-5 rounded-xl bg-white/3 border border-white/8 grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
            {[
              { label: 'Skills', value: result.skills_score },
              { label: 'Keywords', value: result.keyword_score },
              { label: 'Experience', value: result.experience_score },
              { label: 'Job Alignment', value: result.job_alignment_score },
            ].map(({ label, value }) => (
              <div key={label}>
                <p className="text-gray-500 text-xs mb-2">{label}</p>
                <ScoreCircle score={value} size={70} strokeWidth={6} />
              </div>
            ))}
          </div>

          {/* Recommendations */}
          {result.recommendations && result.recommendations.length > 0 && (
            <div>
              <h2 className="text-white font-semibold mb-3">
                Recommendations to Improve Match
              </h2>
              <div className="space-y-3">
                {result.recommendations.map((rec, i) => (
                  <ATSRecommendationCard key={i} recommendation={rec} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
