import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import resumeService from '../../services/resume.service'

function ContactLine({ icon, value }) {
  if (!value) return null
  return (
    <span className="flex items-center gap-1.5 text-gray-600 text-xs">
      <span>{icon}</span>
      <span className="truncate max-w-[160px]">{value}</span>
    </span>
  )
}

function Section({ title, children }) {
  return (
    <div className="mb-5">
      <div className="flex items-center gap-2 mb-2">
        <h2 className="text-gray-900 text-sm font-bold uppercase tracking-widest">{title}</h2>
        <div className="flex-1 h-px bg-gray-300" />
      </div>
      {children}
    </div>
  )
}

function EducationItem({ edu }) {
  return (
    <div className="mb-2">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-gray-900 text-xs font-semibold">{edu.institution}</p>
          <p className="text-gray-700 text-xs">{edu.degree}{edu.field_of_study ? ` in ${edu.field_of_study}` : ''}</p>
        </div>
        <div className="text-right text-xs text-gray-500">
          {edu.start_date && <p>{edu.start_date} – {edu.end_date || 'Present'}</p>}
          {edu.cgpa && <p>CGPA: {edu.cgpa}</p>}
        </div>
      </div>
      {(edu.coursework || []).length > 0 && (
        <p className="text-gray-500 text-xs mt-0.5">Coursework: {edu.coursework.join(', ')}</p>
      )}
    </div>
  )
}

function ProjectItem({ proj }) {
  return (
    <div className="mb-3">
      <div className="flex items-start justify-between">
        <p className="text-gray-900 text-xs font-semibold">{proj.name}</p>
        <div className="flex gap-2 text-xs text-blue-600">
          {proj.github_url && <a href={proj.github_url} target="_blank" rel="noreferrer" className="hover:underline">GitHub</a>}
          {proj.live_url && <a href={proj.live_url} target="_blank" rel="noreferrer" className="hover:underline">Live</a>}
        </div>
      </div>
      {(proj.tech_stack || []).length > 0 && (
        <p className="text-gray-600 text-xs mb-0.5">
          <span className="font-medium">Tech:</span> {proj.tech_stack.join(' · ')}
        </p>
      )}
      {proj.description && <p className="text-gray-700 text-xs leading-snug">{proj.description}</p>}
      {proj.contributions && <p className="text-gray-700 text-xs">• {proj.contributions}</p>}
      {proj.results && <p className="text-gray-700 text-xs">• <span className="font-medium">Impact:</span> {proj.results}</p>}
    </div>
  )
}

function ExperienceItem({ exp }) {
  return (
    <div className="mb-3">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-gray-900 text-xs font-semibold">{exp.role}</p>
          <p className="text-gray-700 text-xs">{exp.company}{exp.location ? ` — ${exp.location}` : ''}</p>
        </div>
        <p className="text-gray-500 text-xs">{exp.start_date} – {exp.end_date || 'Present'}</p>
      </div>
      {(exp.responsibilities || []).map((r, i) => (
        <p key={i} className="text-gray-700 text-xs leading-snug mt-0.5">• {r}</p>
      ))}
      {(exp.achievements || []).map((a, i) => (
        <p key={i} className="text-gray-700 text-xs leading-snug mt-0.5">• {a}</p>
      ))}
    </div>
  )
}

function SkillsBlock({ skills }) {
  const categories = [
    ['programming', 'Languages'],
    ['web_dev', 'Web'],
    ['database', 'Database'],
    ['ai_ml', 'AI/ML'],
    ['data_analytics', 'Analytics'],
    ['cloud', 'Cloud'],
    ['tools', 'Tools'],
    ['other', 'Other'],
  ]
  const lines = categories
    .filter(([key]) => (skills[key] || []).length > 0)
    .map(([key, label]) => `${label}: ${(skills[key] || []).join(', ')}`)

  return (
    <div className="space-y-0.5">
      {lines.map((line, i) => <p key={i} className="text-gray-700 text-xs leading-snug">{line}</p>)}
    </div>
  )
}

export default function ResumePreview() {
  const { resumeId } = useParams()
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    resumeService.get(resumeId)
      .then(({ data: res }) => {
        const latestVersion = res.versions?.[res.versions.length - 1]
        setData({ ...res, parsed: latestVersion?.parsed_data || {} })
      })
      .catch(() => toast.error('Failed to load resume'))
      .finally(() => setLoading(false))
  }, [resumeId])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (!data) {
    return (
      <div className="text-center py-20">
        <p className="text-gray-400">Resume not found.</p>
        <button onClick={() => navigate('/resume')} className="mt-3 text-blue-400 text-sm hover:underline">Back to Resumes</button>
      </div>
    )
  }

  const pd = data.parsed || {}
  const contact = pd.contact || {}
  const skills = pd.skills || {}
  const education = pd.education || []
  const projects = pd.projects || []
  const experience = pd.experience || []
  const certifications = pd.certifications || []
  const achievements = pd.achievements || []

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Controls */}
      <div className="flex items-center justify-between mb-4">
        <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-gray-400 hover:text-white text-sm transition-colors">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back
        </button>
        <div className="flex gap-3">
          <button
            onClick={() => navigate(`/resume/${resumeId}/builder`)}
            className="px-4 py-2 rounded-xl border border-white/10 text-gray-300 text-sm hover:bg-white/5"
          >
            Edit
          </button>
          <button
            onClick={() => window.print()}
            className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium"
          >
            Print / Export PDF
          </button>
        </div>
      </div>

      {/* A4-ish resume sheet */}
      <div
        id="resume-sheet"
        className="bg-white shadow-2xl rounded-xl overflow-hidden"
        style={{ fontFamily: "'Times New Roman', Times, serif" }}
      >
        <div className="p-8">
          {/* Header */}
          <div className="text-center mb-4 pb-3 border-b-2 border-gray-800">
            <h1 className="text-xl font-bold text-gray-900 tracking-wide uppercase">
              {contact.name || data.title}
            </h1>
            <div className="flex flex-wrap justify-center gap-3 mt-1.5">
              <ContactLine icon="✉" value={contact.email} />
              <ContactLine icon="📱" value={contact.phone} />
              <ContactLine icon="📍" value={contact.location} />
              <ContactLine icon="🔗" value={contact.linkedin} />
              <ContactLine icon="💻" value={contact.github} />
              {contact.portfolio && <ContactLine icon="🌐" value={contact.portfolio} />}
            </div>
          </div>

          {/* Summary */}
          {pd.summary && (
            <Section title="Professional Summary">
              <p className="text-gray-700 text-xs leading-snug">{pd.summary}</p>
            </Section>
          )}

          {/* Education */}
          {education.length > 0 && (
            <Section title="Education">
              {education.map((edu, i) => <EducationItem key={i} edu={edu} />)}
            </Section>
          )}

          {/* Skills */}
          {Object.values(skills).some((v) => v?.length > 0) && (
            <Section title="Technical Skills">
              <SkillsBlock skills={skills} />
            </Section>
          )}

          {/* Projects */}
          {projects.length > 0 && (
            <Section title="Projects">
              {projects.map((p, i) => <ProjectItem key={i} proj={p} />)}
            </Section>
          )}

          {/* Experience */}
          {experience.length > 0 && (
            <Section title="Experience">
              {experience.map((exp, i) => <ExperienceItem key={i} exp={exp} />)}
            </Section>
          )}

          {/* Certifications */}
          {certifications.length > 0 && (
            <Section title="Certifications">
              {certifications.map((cert, i) => (
                <div key={i} className="flex justify-between items-center text-xs mb-0.5">
                  <span className="text-gray-800">• {cert.name}{cert.issuer ? ` — ${cert.issuer}` : ''}</span>
                  <span className="text-gray-500">{cert.date}</span>
                </div>
              ))}
            </Section>
          )}

          {/* Achievements */}
          {achievements.length > 0 && (
            <Section title="Achievements">
              {achievements.map((a, i) => (
                <p key={i} className="text-gray-700 text-xs">• {a}</p>
              ))}
            </Section>
          )}
        </div>
      </div>

      <style>{`
        @media print {
          body * { visibility: hidden !important; }
          #resume-sheet, #resume-sheet * { visibility: visible !important; }
          #resume-sheet { position: absolute; left: 0; top: 0; width: 100%; box-shadow: none !important; border-radius: 0 !important; }
        }
      `}</style>
    </div>
  )
}
