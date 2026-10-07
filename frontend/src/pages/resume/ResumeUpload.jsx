import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import resumeService from '../../services/resume.service'

const MAX_SIZE_MB = 5
const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024
const ALLOWED_TYPES = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
const ALLOWED_EXT = ['.pdf', '.docx']

function SkillsList({ skills = {} }) {
  const allSkills = Object.entries(skills).flatMap(([cat, arr]) =>
    (arr || []).map((s) => ({ skill: s, cat }))
  )
  if (!allSkills.length) return <p className="text-gray-500 text-sm">No skills detected</p>
  return (
    <div className="flex flex-wrap gap-2">
      {allSkills.map(({ skill }, i) => (
        <span key={i} className="px-2.5 py-1 rounded-lg bg-blue-900/30 text-blue-300 text-xs border border-blue-500/20">
          {skill}
        </span>
      ))}
    </div>
  )
}

function SectionBlock({ title, children }) {
  return (
    <div className="mb-6">
      <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
        <span className="w-1.5 h-4 rounded-full bg-blue-500 inline-block" />
        {title}
      </h3>
      {children}
    </div>
  )
}

export default function ResumeUpload() {
  const navigate = useNavigate()
  const [dragging, setDragging] = useState(false)
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [parsed, setParsed] = useState(null)
  const [resumeId, setResumeId] = useState(null)
  const [title, setTitle] = useState('My Resume')
  const [saving, setSaving] = useState(false)

  const validateFile = (f) => {
    const ext = f.name.slice(f.name.lastIndexOf('.')).toLowerCase()
    if (!ALLOWED_EXT.includes(ext)) {
      toast.error('Only PDF and DOCX files are allowed')
      return false
    }
    if (f.size > MAX_SIZE_BYTES) {
      toast.error(`File must be under ${MAX_SIZE_MB} MB`)
      return false
    }
    return true
  }

  const handleFileDrop = useCallback((e) => {
    e.preventDefault()
    setDragging(false)
    const f = e.dataTransfer?.files?.[0]
    if (f && validateFile(f)) setFile(f)
  }, [])

  const handleFileChange = (e) => {
    const f = e.target.files?.[0]
    if (f && validateFile(f)) setFile(f)
  }

  const handleUpload = async () => {
    if (!file) return
    setUploading(true)
    setUploadProgress(0)
    try {
      const { data } = await resumeService.upload(file, title, setUploadProgress)
      setParsed(data.parsed_data)
      setResumeId(data.resume_id)
      toast.success('Resume parsed successfully!')
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const handleSave = async () => {
    if (!resumeId) return
    setSaving(true)
    try {
      await resumeService.update(resumeId, { title, parsed_data: parsed })
      toast.success('Resume saved!')
      navigate(`/resume`)
    } catch {
      toast.error('Failed to save resume')
    } finally {
      setSaving(false)
    }
  }

  const updateContact = (field, value) =>
    setParsed((p) => ({ ...p, contact: { ...(p.contact || {}), [field]: value } }))

  const fmtSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
  }

  return (
    <div className="max-w-3xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white">Upload Resume</h1>
        <p className="text-gray-400 text-sm mt-1">Upload a PDF or DOCX file and we'll parse it automatically</p>
      </div>

      {!parsed ? (
        <div className="space-y-5">
          {/* Title */}
          <div>
            <label className="block text-sm text-gray-400 mb-1.5">Resume Title</label>
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-blue-500"
              placeholder="My Resume"
            />
          </div>

          {/* Drop zone */}
          <div
            onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
            onDragLeave={() => setDragging(false)}
            onDrop={handleFileDrop}
            className={`relative rounded-2xl border-2 border-dashed transition-all p-10 text-center ${
              dragging ? 'border-blue-500 bg-blue-900/10' : 'border-white/10 bg-white/3 hover:border-white/20'
            }`}
          >
            <input
              type="file"
              accept=".pdf,.docx"
              onChange={handleFileChange}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            <div className="flex flex-col items-center gap-3 pointer-events-none">
              <div className="w-14 h-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center">
                <svg className="w-6 h-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
              </div>
              <div>
                <p className="text-gray-300 font-medium">Drag & drop your resume here</p>
                <p className="text-gray-500 text-sm mt-1">or click to browse — PDF or DOCX, max {MAX_SIZE_MB} MB</p>
              </div>
            </div>
          </div>

          {/* Selected file info */}
          {file && (
            <div className="flex items-center gap-3 p-4 rounded-xl bg-white/5 border border-white/10">
              <div className="w-8 h-8 rounded-lg bg-blue-900/40 flex items-center justify-center">
                <svg className="w-4 h-4 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-white text-sm truncate">{file.name}</p>
                <p className="text-gray-500 text-xs">{fmtSize(file.size)}</p>
              </div>
              <button onClick={() => setFile(null)} className="text-gray-500 hover:text-red-400 text-xs">Remove</button>
            </div>
          )}

          {uploading && (
            <div>
              <div className="flex justify-between text-xs text-gray-400 mb-1">
                <span>Uploading & parsing…</span>
                <span>{uploadProgress}%</span>
              </div>
              <div className="h-2 bg-white/8 rounded-full overflow-hidden">
                <div className="h-full bg-blue-500 rounded-full transition-all" style={{ width: `${uploadProgress}%` }} />
              </div>
            </div>
          )}

          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="w-full py-3 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-medium text-sm disabled:opacity-40 disabled:cursor-not-allowed transition-all"
          >
            {uploading ? 'Parsing…' : 'Upload & Parse'}
          </button>
        </div>
      ) : (
        /* ─── Parsed data editor ─── */
        <div className="space-y-6">
          <div className="flex items-center justify-between p-4 rounded-xl bg-emerald-900/20 border border-emerald-500/30">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span className="text-emerald-400 font-medium text-sm">Resume parsed successfully</span>
            </div>
            <button onClick={() => { setFile(null); setParsed(null) }} className="text-gray-500 hover:text-gray-300 text-xs">
              Upload different file
            </button>
          </div>

          {/* Title */}
          <div>
            <label className="block text-sm text-gray-400 mb-1.5">Resume Title</label>
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* Contact Info */}
          <SectionBlock title="Personal Info">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {['name', 'email', 'phone', 'location', 'linkedin', 'github', 'portfolio'].map((field) => (
                <div key={field}>
                  <label className="block text-xs text-gray-500 mb-1 capitalize">{field}</label>
                  <input
                    value={parsed?.contact?.[field] || ''}
                    onChange={(e) => updateContact(field, e.target.value)}
                    className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
                    placeholder={`Your ${field}`}
                  />
                </div>
              ))}
            </div>
          </SectionBlock>

          {/* Skills */}
          <SectionBlock title="Skills Detected">
            <SkillsList skills={parsed?.skills || {}} />
          </SectionBlock>

          {/* Education */}
          <SectionBlock title="Education">
            {(parsed?.education || []).length === 0 ? (
              <p className="text-gray-500 text-sm">No education detected</p>
            ) : (
              <div className="space-y-3">
                {(parsed.education || []).map((edu, i) => (
                  <div key={i} className="p-3 rounded-lg bg-white/5 border border-white/8">
                    <p className="text-white text-sm font-medium">{edu.institution || 'Institution'}</p>
                    <p className="text-gray-400 text-xs mt-0.5">{edu.degree || edu.field_of_study || 'Degree'}</p>
                    {edu.cgpa && <p className="text-gray-500 text-xs mt-0.5">CGPA: {edu.cgpa}</p>}
                  </div>
                ))}
              </div>
            )}
          </SectionBlock>

          {/* Projects */}
          <SectionBlock title="Projects">
            {(parsed?.projects || []).length === 0 ? (
              <p className="text-gray-500 text-sm">No projects detected</p>
            ) : (
              <div className="space-y-3">
                {(parsed.projects || []).map((proj, i) => (
                  <div key={i} className="p-3 rounded-lg bg-white/5 border border-white/8">
                    <p className="text-white text-sm font-medium">{proj.name}</p>
                    {proj.description && <p className="text-gray-400 text-xs mt-1 line-clamp-2">{proj.description}</p>}
                    {proj.tech_stack?.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {proj.tech_stack.map((t, j) => (
                          <span key={j} className="text-xs px-1.5 py-0.5 rounded bg-white/8 text-gray-400">{t}</span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </SectionBlock>

          {/* Experience */}
          <SectionBlock title="Experience">
            {(parsed?.experience || []).length === 0 ? (
              <p className="text-gray-500 text-sm">No experience detected</p>
            ) : (
              <div className="space-y-3">
                {(parsed.experience || []).map((exp, i) => (
                  <div key={i} className="p-3 rounded-lg bg-white/5 border border-white/8">
                    <p className="text-white text-sm font-medium">{exp.role || exp.company}</p>
                    {exp.company && exp.role && <p className="text-gray-400 text-xs">{exp.company}</p>}
                    {(exp.start_date || exp.end_date) && (
                      <p className="text-gray-500 text-xs">{exp.start_date} – {exp.end_date}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </SectionBlock>

          {/* Certifications */}
          <SectionBlock title="Certifications">
            {(parsed?.certifications || []).length === 0 ? (
              <p className="text-gray-500 text-sm">No certifications detected</p>
            ) : (
              <ul className="space-y-1">
                {(parsed.certifications || []).map((cert, i) => (
                  <li key={i} className="text-gray-300 text-sm flex items-start gap-2">
                    <span className="text-blue-400 mt-0.5">•</span>
                    {cert.name}{cert.issuer ? ` — ${cert.issuer}` : ''}
                  </li>
                ))}
              </ul>
            )}
          </SectionBlock>

          {/* Achievements */}
          <SectionBlock title="Achievements">
            {(parsed?.achievements || []).length === 0 ? (
              <p className="text-gray-500 text-sm">No achievements detected</p>
            ) : (
              <ul className="space-y-1">
                {(parsed.achievements || []).map((a, i) => (
                  <li key={i} className="text-gray-300 text-sm flex items-start gap-2">
                    <span className="text-blue-400 mt-0.5">•</span>{a}
                  </li>
                ))}
              </ul>
            )}
          </SectionBlock>

          <div className="flex gap-3 pt-2">
            <button
              onClick={() => navigate('/resume')}
              className="flex-1 py-2.5 rounded-xl border border-white/10 text-gray-400 text-sm hover:bg-white/5 transition-all"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={saving}
              className="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-medium text-sm disabled:opacity-40 transition-all"
            >
              {saving ? 'Saving…' : 'Save Resume'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
