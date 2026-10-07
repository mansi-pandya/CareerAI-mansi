import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import resumeService from '../../services/resume.service'

// ─── Helpers ────────────────────────────────────────────────────────────────

const SKILL_CATEGORIES = [
  { key: 'programming', label: 'Programming Languages' },
  { key: 'web_dev', label: 'Web Development' },
  { key: 'database', label: 'Databases' },
  { key: 'ai_ml', label: 'AI / ML' },
  { key: 'data_analytics', label: 'Data Analytics' },
  { key: 'cloud', label: 'Cloud & DevOps' },
  { key: 'tools', label: 'Tools' },
]

const TABS = [
  { id: 'contact', label: 'Personal Info' },
  { id: 'education', label: 'Education' },
  { id: 'skills', label: 'Skills' },
  { id: 'projects', label: 'Projects' },
  { id: 'experience', label: 'Experience' },
  { id: 'certifications', label: 'Certifications' },
  { id: 'achievements', label: 'Achievements' },
]

const emptyEducation = () => ({
  institution: '', degree: '', field_of_study: '', start_date: '', end_date: '', cgpa: '', coursework: [],
})
const emptyProject = () => ({
  name: '', description: '', tech_stack: [], github_url: '', live_url: '', contributions: '', results: '',
})
const emptyExperience = () => ({
  company: '', role: '', start_date: '', end_date: '', location: '', responsibilities: [], achievements: [],
})
const emptyCert = () => ({ name: '', issuer: '', date: '', url: '' })

// ─── Sub-components ───────────────────────────────────────────────────────────

function Field({ label, value, onChange, type = 'text', placeholder = '', className = '' }) {
  return (
    <div className={className}>
      <label className="block text-xs text-gray-500 mb-1">{label}</label>
      {type === 'textarea' ? (
        <textarea
          value={value || ''}
          onChange={(e) => onChange(e.target.value)}
          rows={3}
          placeholder={placeholder}
          className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500 resize-none"
        />
      ) : (
        <input
          type={type}
          value={value || ''}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
        />
      )}
    </div>
  )
}

function TagInput({ label, tags = [], onChange, placeholder = 'Add item, press Enter' }) {
  const [input, setInput] = useState('')

  const add = () => {
    const val = input.trim()
    if (val && !tags.includes(val)) onChange([...tags, val])
    setInput('')
  }

  const remove = (i) => onChange(tags.filter((_, idx) => idx !== i))

  return (
    <div>
      <label className="block text-xs text-gray-500 mb-1">{label}</label>
      <div className="flex flex-wrap gap-1.5 mb-2">
        {tags.map((t, i) => (
          <span key={i} className="flex items-center gap-1 px-2 py-0.5 rounded-md bg-blue-900/40 text-blue-300 text-xs border border-blue-500/20">
            {t}
            <button onClick={() => remove(i)} className="text-blue-400 hover:text-red-400 ml-0.5">×</button>
          </span>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); add() } }}
          placeholder={placeholder}
          className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-white text-sm focus:outline-none focus:border-blue-500"
        />
        <button onClick={add} className="px-3 py-1.5 rounded-lg bg-blue-900/40 text-blue-300 text-xs hover:bg-blue-900/60">Add</button>
      </div>
    </div>
  )
}

function BulletListInput({ label, items = [], onChange, placeholder = '' }) {
  const [input, setInput] = useState('')

  const add = () => {
    const val = input.trim()
    if (val) onChange([...items, val])
    setInput('')
  }

  return (
    <div>
      <label className="block text-xs text-gray-500 mb-1">{label}</label>
      <div className="space-y-1.5 mb-2">
        {items.map((item, i) => (
          <div key={i} className="flex items-start gap-2 group">
            <span className="text-blue-400 mt-1 text-xs">•</span>
            <p className="flex-1 text-sm text-gray-300 leading-snug">{item}</p>
            <button
              onClick={() => onChange(items.filter((_, idx) => idx !== i))}
              className="opacity-0 group-hover:opacity-100 text-red-400 text-xs transition-opacity"
            >
              ×
            </button>
          </div>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); add() } }}
          placeholder={placeholder}
          className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-white text-sm focus:outline-none focus:border-blue-500"
        />
        <button onClick={add} className="px-3 py-1.5 rounded-lg bg-white/8 text-gray-300 text-xs hover:bg-white/12">Add</button>
      </div>
    </div>
  )
}

function AIImproveBtn({ resumeId, section, field, currentText, onImproved }) {
  const [loading, setLoading] = useState(false)

  const handleImprove = async () => {
    if (!currentText?.trim()) { toast.error('Enter some text first'); return }
    setLoading(true)
    try {
      const { data } = await resumeService.aiImprove(resumeId, section, field, currentText)
      if (data.improved_text && data.improved_text !== currentText) {
        onImproved(data.improved_text)
        toast.success('Text improved!')
      } else {
        toast(data.message || 'No improvements suggested', { icon: 'ℹ️' })
      }
    } catch {
      toast.error('AI improvement failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <button
      onClick={handleImprove}
      disabled={loading || !resumeId}
      title={resumeId ? 'Improve with AI' : 'Save resume first to use AI'}
      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-purple-900/30 hover:bg-purple-900/50 text-purple-300 text-xs border border-purple-500/20 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
    >
      {loading ? (
        <svg className="w-3 h-3 animate-spin" viewBox="0 0 24 24" fill="none">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      ) : (
        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      )}
      {loading ? 'Improving…' : 'Improve with AI'}
    </button>
  )
}

// ─── Tab Panels ───────────────────────────────────────────────────────────────

function ContactPanel({ data, onChange }) {
  const set = (field) => (val) => onChange({ ...data, [field]: val })
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <Field label="Full Name" value={data.name} onChange={set('name')} placeholder="Jane Doe" className="sm:col-span-2" />
      <Field label="Email" value={data.email} onChange={set('email')} type="email" placeholder="jane@example.com" />
      <Field label="Phone" value={data.phone} onChange={set('phone')} placeholder="+91 9876543210" />
      <Field label="Location" value={data.location} onChange={set('location')} placeholder="Mumbai, India" />
      <Field label="LinkedIn URL" value={data.linkedin} onChange={set('linkedin')} placeholder="linkedin.com/in/jane" />
      <Field label="GitHub URL" value={data.github} onChange={set('github')} placeholder="github.com/jane" />
      <Field label="Portfolio / Website" value={data.portfolio} onChange={set('portfolio')} placeholder="https://jane.dev" />
    </div>
  )
}

function EducationPanel({ items, onChange, resumeId }) {
  const update = (i, field, val) => {
    const next = items.map((item, idx) => idx === i ? { ...item, [field]: val } : item)
    onChange(next)
  }
  const remove = (i) => onChange(items.filter((_, idx) => idx !== i))
  const add = () => onChange([...items, emptyEducation()])

  return (
    <div className="space-y-5">
      {items.map((edu, i) => (
        <div key={i} className="p-4 rounded-xl bg-white/3 border border-white/8 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-white text-sm font-medium">Education {i + 1}</span>
            <button onClick={() => remove(i)} className="text-red-400 text-xs hover:text-red-300">Remove</button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Field label="Institution" value={edu.institution} onChange={(v) => update(i, 'institution', v)} placeholder="IIT Bombay" className="sm:col-span-2" />
            <Field label="Degree" value={edu.degree} onChange={(v) => update(i, 'degree', v)} placeholder="B.Tech" />
            <Field label="Field of Study" value={edu.field_of_study} onChange={(v) => update(i, 'field_of_study', v)} placeholder="Computer Science" />
            <Field label="Start Date" value={edu.start_date} onChange={(v) => update(i, 'start_date', v)} placeholder="Aug 2020" />
            <Field label="End Date" value={edu.end_date} onChange={(v) => update(i, 'end_date', v)} placeholder="May 2024" />
            <Field label="CGPA" value={edu.cgpa} onChange={(v) => update(i, 'cgpa', v)} placeholder="8.5/10" />
          </div>
          <TagInput
            label="Relevant Coursework"
            tags={edu.coursework || []}
            onChange={(v) => update(i, 'coursework', v)}
            placeholder="Data Structures, Algorithms…"
          />
        </div>
      ))}
      <button onClick={add} className="w-full py-2.5 rounded-xl border border-dashed border-white/10 text-gray-500 hover:text-gray-300 hover:border-white/20 text-sm transition-all">
        + Add Education
      </button>
    </div>
  )
}

function SkillsPanel({ data, onChange }) {
  const setCategory = (cat) => (tags) => onChange({ ...data, [cat]: tags })
  return (
    <div className="space-y-5">
      {SKILL_CATEGORIES.map(({ key, label }) => (
        <TagInput
          key={key}
          label={label}
          tags={data[key] || []}
          onChange={setCategory(key)}
          placeholder={`Add ${label} skill…`}
        />
      ))}
    </div>
  )
}

function ProjectsPanel({ items, onChange, resumeId }) {
  const update = (i, field, val) => {
    const next = items.map((item, idx) => idx === i ? { ...item, [field]: val } : item)
    onChange(next)
  }
  const remove = (i) => onChange(items.filter((_, idx) => idx !== i))
  const add = () => onChange([...items, emptyProject()])

  return (
    <div className="space-y-5">
      {items.map((proj, i) => (
        <div key={i} className="p-4 rounded-xl bg-white/3 border border-white/8 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-white text-sm font-medium">Project {i + 1}</span>
            <button onClick={() => remove(i)} className="text-red-400 text-xs">Remove</button>
          </div>
          <Field label="Project Name" value={proj.name} onChange={(v) => update(i, 'name', v)} placeholder="My Awesome App" />
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="text-xs text-gray-500">Description</label>
              <AIImproveBtn
                resumeId={resumeId}
                section="projects"
                field="description"
                currentText={proj.description}
                onImproved={(v) => update(i, 'description', v)}
              />
            </div>
            <textarea
              value={proj.description || ''}
              onChange={(e) => update(i, 'description', e.target.value)}
              rows={3}
              placeholder="What does this project do and what problem does it solve?"
              className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500 resize-none"
            />
          </div>
          <TagInput label="Tech Stack" tags={proj.tech_stack || []} onChange={(v) => update(i, 'tech_stack', v)} placeholder="React, Python, PostgreSQL…" />
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Field label="GitHub URL" value={proj.github_url} onChange={(v) => update(i, 'github_url', v)} placeholder="github.com/you/project" />
            <Field label="Live URL" value={proj.live_url} onChange={(v) => update(i, 'live_url', v)} placeholder="https://project.vercel.app" />
          </div>
          <Field label="Your Contributions" value={proj.contributions} onChange={(v) => update(i, 'contributions', v)} type="textarea" placeholder="What did you specifically build or design?" />
          <Field label="Results / Impact" value={proj.results} onChange={(v) => update(i, 'results', v)} placeholder="e.g. 500+ users, 40% faster load time" />
        </div>
      ))}
      <button onClick={add} className="w-full py-2.5 rounded-xl border border-dashed border-white/10 text-gray-500 hover:text-gray-300 hover:border-white/20 text-sm transition-all">
        + Add Project
      </button>
    </div>
  )
}

function ExperiencePanel({ items, onChange, resumeId }) {
  const update = (i, field, val) => {
    const next = items.map((item, idx) => idx === i ? { ...item, [field]: val } : item)
    onChange(next)
  }
  const remove = (i) => onChange(items.filter((_, idx) => idx !== i))
  const add = () => onChange([...items, emptyExperience()])

  return (
    <div className="space-y-5">
      {items.map((exp, i) => (
        <div key={i} className="p-4 rounded-xl bg-white/3 border border-white/8 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-white text-sm font-medium">Experience {i + 1}</span>
            <button onClick={() => remove(i)} className="text-red-400 text-xs">Remove</button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Field label="Company / Organization" value={exp.company} onChange={(v) => update(i, 'company', v)} placeholder="Acme Corp" />
            <Field label="Role / Title" value={exp.role} onChange={(v) => update(i, 'role', v)} placeholder="Software Engineer Intern" />
            <Field label="Start Date" value={exp.start_date} onChange={(v) => update(i, 'start_date', v)} placeholder="Jun 2023" />
            <Field label="End Date" value={exp.end_date} onChange={(v) => update(i, 'end_date', v)} placeholder="Aug 2023 or Present" />
            <Field label="Location" value={exp.location} onChange={(v) => update(i, 'location', v)} placeholder="Remote / Mumbai" />
          </div>
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-gray-500">Responsibilities</span>
              <AIImproveBtn
                resumeId={resumeId}
                section="experience"
                field="responsibilities"
                currentText={(exp.responsibilities || []).join('\n')}
                onImproved={(v) => update(i, 'responsibilities', v.split('\n').filter(Boolean))}
              />
            </div>
            <BulletListInput
              label=""
              items={exp.responsibilities || []}
              onChange={(v) => update(i, 'responsibilities', v)}
              placeholder="Developed a REST API that…"
            />
          </div>
          <BulletListInput
            label="Achievements"
            items={exp.achievements || []}
            onChange={(v) => update(i, 'achievements', v)}
            placeholder="Reduced query time by 50%…"
          />
        </div>
      ))}
      <button onClick={add} className="w-full py-2.5 rounded-xl border border-dashed border-white/10 text-gray-500 hover:text-gray-300 hover:border-white/20 text-sm transition-all">
        + Add Experience
      </button>
    </div>
  )
}

function CertificationsPanel({ items, onChange }) {
  const update = (i, field, val) => onChange(items.map((item, idx) => idx === i ? { ...item, [field]: val } : item))
  const remove = (i) => onChange(items.filter((_, idx) => idx !== i))
  const add = () => onChange([...items, emptyCert()])

  return (
    <div className="space-y-4">
      {items.map((cert, i) => (
        <div key={i} className="p-4 rounded-xl bg-white/3 border border-white/8 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-white text-sm font-medium">Certification {i + 1}</span>
            <button onClick={() => remove(i)} className="text-red-400 text-xs">Remove</button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Field label="Certification Name" value={cert.name} onChange={(v) => update(i, 'name', v)} placeholder="AWS Solutions Architect" className="sm:col-span-2" />
            <Field label="Issuing Organization" value={cert.issuer} onChange={(v) => update(i, 'issuer', v)} placeholder="Amazon Web Services" />
            <Field label="Date" value={cert.date} onChange={(v) => update(i, 'date', v)} placeholder="Mar 2024" />
            <Field label="Credential URL" value={cert.url} onChange={(v) => update(i, 'url', v)} placeholder="https://verify.aws.com/…" className="sm:col-span-2" />
          </div>
        </div>
      ))}
      <button onClick={add} className="w-full py-2.5 rounded-xl border border-dashed border-white/10 text-gray-500 hover:text-gray-300 hover:border-white/20 text-sm transition-all">
        + Add Certification
      </button>
    </div>
  )
}

function AchievementsPanel({ items, onChange, resumeId }) {
  const [input, setInput] = useState('')
  const add = () => {
    const val = input.trim()
    if (val) onChange([...items, val])
    setInput('')
  }
  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <p className="text-gray-400 text-sm">List hackathon wins, academic prizes, rankings, or notable recognitions.</p>
        <AIImproveBtn
          resumeId={resumeId}
          section="achievements"
          field="list"
          currentText={items.join('\n')}
          onImproved={(v) => onChange(v.split('\n').filter(Boolean))}
        />
      </div>
      <div className="space-y-2 mb-3">
        {items.map((item, i) => (
          <div key={i} className="flex items-start gap-2 group p-2.5 rounded-lg bg-white/3 border border-white/8">
            <span className="text-yellow-400 mt-0.5">🏆</span>
            <p className="flex-1 text-sm text-gray-300">{item}</p>
            <button onClick={() => onChange(items.filter((_, idx) => idx !== i))} className="opacity-0 group-hover:opacity-100 text-red-400 text-xs">×</button>
          </div>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); add() } }}
          placeholder="Won 1st place at HackIIT 2023…"
          className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
        />
        <button onClick={add} className="px-4 py-2 rounded-lg bg-white/8 text-gray-300 text-sm hover:bg-white/12">Add</button>
      </div>
    </div>
  )
}

// ─── Mini Preview ─────────────────────────────────────────────────────────────

function MiniPreview({ form }) {
  const contact = form.contact || {}
  const skills = form.skills || {}
  const allSkills = Object.values(skills).flat().filter(Boolean).slice(0, 12)

  return (
    <div className="text-xs text-gray-400 space-y-3 overflow-hidden">
      {/* Contact */}
      <div className="text-center pb-2 border-b border-white/8">
        <p className="text-white font-semibold text-sm">{contact.name || 'Your Name'}</p>
        <p className="text-gray-500 mt-0.5 text-xs">
          {[contact.email, contact.phone, contact.location].filter(Boolean).join(' · ')}
        </p>
        <p className="text-blue-400 text-xs mt-0.5">
          {[contact.linkedin, contact.github].filter(Boolean).join(' · ')}
        </p>
      </div>
      {/* Education */}
      {(form.education || []).length > 0 && (
        <div>
          <p className="text-gray-300 font-semibold uppercase text-xs tracking-wider mb-1 border-b border-white/5 pb-1">Education</p>
          {(form.education || []).slice(0, 2).map((edu, i) => (
            <div key={i} className="mb-1">
              <p className="text-gray-300 font-medium">{edu.institution || '—'}</p>
              <p className="text-gray-500">{edu.degree} {edu.field_of_study}</p>
            </div>
          ))}
        </div>
      )}
      {/* Skills */}
      {allSkills.length > 0 && (
        <div>
          <p className="text-gray-300 font-semibold uppercase text-xs tracking-wider mb-1.5 border-b border-white/5 pb-1">Skills</p>
          <div className="flex flex-wrap gap-1">
            {allSkills.map((s, i) => (
              <span key={i} className="px-1.5 py-0.5 rounded bg-white/8 text-gray-400">{s}</span>
            ))}
          </div>
        </div>
      )}
      {/* Projects */}
      {(form.projects || []).length > 0 && (
        <div>
          <p className="text-gray-300 font-semibold uppercase text-xs tracking-wider mb-1 border-b border-white/5 pb-1">Projects</p>
          {(form.projects || []).slice(0, 3).map((p, i) => (
            <div key={i} className="mb-1">
              <p className="text-gray-300 font-medium">{p.name || 'Untitled'}</p>
              {(p.tech_stack || []).length > 0 && (
                <p className="text-gray-500">{p.tech_stack.join(', ')}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ─── Main Component ───────────────────────────────────────────────────────────

const INITIAL_FORM = {
  title: 'My Resume',
  contact: { name: '', email: '', phone: '', location: '', linkedin: '', github: '', portfolio: '' },
  education: [],
  skills: {},
  projects: [],
  experience: [],
  certifications: [],
  achievements: [],
  summary: '',
}

export default function ResumeBuilder() {
  const { resumeId } = useParams()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('contact')
  const [form, setForm] = useState(INITIAL_FORM)
  const [savedId, setSavedId] = useState(resumeId ? parseInt(resumeId) : null)
  const [saving, setSaving] = useState(false)
  const [loading, setLoading] = useState(!!resumeId)

  // Load existing resume if editing
  useEffect(() => {
    if (!resumeId) return
    resumeService.get(resumeId)
      .then(({ data }) => {
        const latestVersion = data.versions?.[data.versions.length - 1]
        const pd = latestVersion?.parsed_data || {}
        setForm({
          title: data.title || 'My Resume',
          contact: pd.contact || INITIAL_FORM.contact,
          education: pd.education || [],
          skills: pd.skills || {},
          projects: pd.projects || [],
          experience: pd.experience || [],
          certifications: pd.certifications || [],
          achievements: pd.achievements || [],
          summary: pd.summary || '',
        })
      })
      .catch(() => toast.error('Failed to load resume'))
      .finally(() => setLoading(false))
  }, [resumeId])

  const setSection = (section) => (val) => setForm((f) => ({ ...f, [section]: val }))

  const handleSave = async (asNewVersion = false) => {
    setSaving(true)
    try {
      const payload = {
        title: form.title,
        contact: form.contact,
        education: form.education,
        skills: form.skills,
        projects: form.projects,
        experience: form.experience,
        certifications: form.certifications,
        achievements: form.achievements,
        summary: form.summary,
      }

      if (savedId && !asNewVersion) {
        await resumeService.update(savedId, { title: form.title, parsed_data: payload })
        toast.success('Resume saved!')
      } else if (savedId && asNewVersion) {
        await resumeService.update(savedId, { parsed_data: payload })
        toast.success('Saved as new version!')
      } else {
        const { data } = await resumeService.createFromBuilder(payload)
        setSavedId(data.id)
        navigate(`/resume/${data.id}/builder`, { replace: true })
        toast.success('Resume created!')
      }
    } catch {
      toast.error('Failed to save resume')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <input
            value={form.title}
            onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
            className="text-xl font-bold bg-transparent text-white border-b border-transparent hover:border-white/20 focus:border-blue-500 focus:outline-none pb-0.5"
          />
          <p className="text-gray-500 text-sm mt-0.5">Resume Builder</p>
        </div>
        <div className="flex gap-2">
          {savedId && (
            <button
              onClick={() => handleSave(true)}
              disabled={saving}
              className="px-4 py-2 rounded-xl border border-white/10 text-gray-300 text-sm hover:bg-white/5 transition-all disabled:opacity-40"
            >
              Save as New Version
            </button>
          )}
          <button
            onClick={() => handleSave(false)}
            disabled={saving}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-sm font-medium disabled:opacity-40 transition-all"
          >
            {saving ? (
              <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
            ) : null}
            {saving ? 'Saving…' : 'Save Resume'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Editor */}
        <div className="lg:col-span-2 space-y-4">
          {/* Tabs */}
          <div className="flex flex-wrap gap-1 p-1 bg-white/5 rounded-xl border border-white/8">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-3 py-1.5 rounded-lg text-sm transition-all ${
                  activeTab === tab.id
                    ? 'bg-blue-600 text-white font-medium'
                    : 'text-gray-400 hover:text-gray-200'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Panel */}
          <div className="p-5 rounded-xl border border-white/10 bg-gray-900/50">
            {activeTab === 'contact' && (
              <ContactPanel data={form.contact} onChange={setSection('contact')} />
            )}
            {activeTab === 'education' && (
              <EducationPanel items={form.education} onChange={setSection('education')} resumeId={savedId} />
            )}
            {activeTab === 'skills' && (
              <SkillsPanel data={form.skills} onChange={setSection('skills')} />
            )}
            {activeTab === 'projects' && (
              <ProjectsPanel items={form.projects} onChange={setSection('projects')} resumeId={savedId} />
            )}
            {activeTab === 'experience' && (
              <ExperiencePanel items={form.experience} onChange={setSection('experience')} resumeId={savedId} />
            )}
            {activeTab === 'certifications' && (
              <CertificationsPanel items={form.certifications} onChange={setSection('certifications')} />
            )}
            {activeTab === 'achievements' && (
              <AchievementsPanel items={form.achievements} onChange={setSection('achievements')} resumeId={savedId} />
            )}
          </div>
        </div>

        {/* Right: Preview */}
        <div className="space-y-4">
          <div className="p-5 rounded-xl border border-white/10 bg-gray-900/50 sticky top-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-white font-semibold text-sm">Live Preview</h3>
              {savedId && (
                <button
                  onClick={() => navigate(`/resume/${savedId}/preview`)}
                  className="text-xs text-blue-400 hover:text-blue-300"
                >
                  Full Preview →
                </button>
              )}
            </div>
            <MiniPreview form={form} />
          </div>

          {savedId && (
            <button
              onClick={() => navigate(`/ats?resume=${savedId}`)}
              className="w-full py-2.5 rounded-xl bg-gradient-to-r from-emerald-600/20 to-teal-600/20 border border-emerald-500/20 text-emerald-400 text-sm hover:from-emerald-600/30 hover:to-teal-600/30 transition-all"
            >
              Check ATS Score →
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
