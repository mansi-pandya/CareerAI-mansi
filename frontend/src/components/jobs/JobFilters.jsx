import { clsx } from 'clsx'

const JOB_TYPES = [
  { value: 'internship', label: 'Internship' },
  { value: 'full_time', label: 'Full-time' },
  { value: 'part_time', label: 'Part-time' },
  { value: 'freelance', label: 'Freelance' },
  { value: 'contract', label: 'Contract' },
  { value: 'apprenticeship', label: 'Apprenticeship' },
]

const WORK_MODES = [
  { value: 'remote', label: 'Remote' },
  { value: 'hybrid', label: 'Hybrid' },
  { value: 'on_site', label: 'On-site' },
]

const LOCATION_PRESETS = [
  { label: 'Anywhere in India', value: 'India' },
  { label: 'Bangalore', value: 'Bangalore' },
  { label: 'Mumbai', value: 'Mumbai' },
  { label: 'Delhi', value: 'Delhi' },
  { label: 'Hyderabad', value: 'Hyderabad' },
  { label: 'Chennai', value: 'Chennai' },
  { label: 'US Remote', value: 'US Remote' },
  { label: 'Worldwide Remote', value: 'Remote' },
]

const SOURCES = [
  { value: '', label: 'All Sources' },
  { value: 'adzuna', label: 'Adzuna' },
  { value: 'demo', label: 'Demo' },
]

function SectionTitle({ children }) {
  return (
    <p className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-3">
      {children}
    </p>
  )
}

function CheckboxItem({ checked, onChange, label }) {
  return (
    <label className="flex items-center gap-2 cursor-pointer group">
      <input
        type="checkbox"
        checked={checked}
        onChange={onChange}
        className="w-3.5 h-3.5 rounded border-white/20 bg-gray-800 accent-blue-500 cursor-pointer"
      />
      <span className="text-sm text-gray-300 group-hover:text-white transition-colors">
        {label}
      </span>
    </label>
  )
}

export default function JobFilters({ filters, onChange }) {
  const {
    jobTypes = [],
    workModes = [],
    location = '',
    salaryMin = '',
    salaryMax = '',
    experienceMin = '',
    skills = [],
    source = '',
  } = filters

  const toggleArray = (key, value) => {
    const arr = filters[key] || []
    const next = arr.includes(value) ? arr.filter((v) => v !== value) : [...arr, value]
    onChange({ ...filters, [key]: next })
  }

  const setField = (key, value) => onChange({ ...filters, [key]: value })

  const addSkill = (skill) => {
    const s = skill.trim()
    if (!s || skills.includes(s)) return
    onChange({ ...filters, skills: [...skills, s] })
  }

  const removeSkill = (skill) => {
    onChange({ ...filters, skills: skills.filter((s) => s !== skill) })
  }

  const handleSkillKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault()
      addSkill(e.target.value)
      e.target.value = ''
    }
  }

  const clearAll = () => {
    onChange({
      jobTypes: [],
      workModes: [],
      location: '',
      salaryMin: '',
      salaryMax: '',
      experienceMin: '',
      skills: [],
      source: '',
    })
  }

  const hasFilters =
    jobTypes.length > 0 ||
    workModes.length > 0 ||
    location ||
    salaryMin ||
    salaryMax ||
    experienceMin ||
    skills.length > 0 ||
    source

  return (
    <div className="space-y-6">
      {/* Clear button */}
      {hasFilters && (
        <button
          onClick={clearAll}
          className="text-xs text-blue-400 hover:text-blue-300 transition-colors"
        >
          Clear all filters
        </button>
      )}

      {/* Job Type */}
      <div>
        <SectionTitle>Job Type</SectionTitle>
        <div className="space-y-2">
          {JOB_TYPES.map((jt) => (
            <CheckboxItem
              key={jt.value}
              checked={jobTypes.includes(jt.value)}
              onChange={() => toggleArray('jobTypes', jt.value)}
              label={jt.label}
            />
          ))}
        </div>
      </div>

      {/* Work Mode */}
      <div>
        <SectionTitle>Work Mode</SectionTitle>
        <div className="space-y-2">
          {WORK_MODES.map((wm) => (
            <CheckboxItem
              key={wm.value}
              checked={workModes.includes(wm.value)}
              onChange={() => toggleArray('workModes', wm.value)}
              label={wm.label}
            />
          ))}
        </div>
      </div>

      {/* Location */}
      <div>
        <SectionTitle>Location</SectionTitle>
        <input
          type="text"
          value={location}
          onChange={(e) => setField('location', e.target.value)}
          placeholder="City or country..."
          className="w-full bg-gray-800 border border-white/10 rounded-lg px-3 py-2 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-blue-500/50 mb-2"
        />
        <div className="flex flex-wrap gap-1.5">
          {LOCATION_PRESETS.map((p) => (
            <button
              key={p.value}
              onClick={() => setField('location', location === p.value ? '' : p.value)}
              className={clsx(
                'px-2 py-1 text-xs rounded-full border transition-colors',
                location === p.value
                  ? 'bg-blue-600/30 border-blue-500/50 text-blue-300'
                  : 'bg-white/5 border-white/10 text-gray-400 hover:border-white/25 hover:text-gray-300',
              )}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Salary Range */}
      <div>
        <SectionTitle>Salary (INR / yr)</SectionTitle>
        <div className="flex gap-2">
          <input
            type="number"
            value={salaryMin}
            onChange={(e) => setField('salaryMin', e.target.value)}
            placeholder="Min"
            className="w-1/2 bg-gray-800 border border-white/10 rounded-lg px-3 py-2 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-blue-500/50"
          />
          <input
            type="number"
            value={salaryMax}
            onChange={(e) => setField('salaryMax', e.target.value)}
            placeholder="Max"
            className="w-1/2 bg-gray-800 border border-white/10 rounded-lg px-3 py-2 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-blue-500/50"
          />
        </div>
      </div>

      {/* Experience */}
      <div>
        <SectionTitle>Min Experience (yrs)</SectionTitle>
        <select
          value={experienceMin}
          onChange={(e) => setField('experienceMin', e.target.value)}
          className="w-full bg-gray-800 border border-white/10 rounded-lg px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-blue-500/50"
        >
          <option value="">Any</option>
          <option value="0">Fresher (0)</option>
          <option value="1">1+ year</option>
          <option value="2">2+ years</option>
          <option value="3">3+ years</option>
          <option value="5">5+ years</option>
          <option value="7">7+ years</option>
        </select>
      </div>

      {/* Skills */}
      <div>
        <SectionTitle>Required Skills</SectionTitle>
        {skills.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-2">
            {skills.map((skill) => (
              <span
                key={skill}
                className="flex items-center gap-1 px-2 py-0.5 text-xs rounded-full bg-blue-900/40 border border-blue-500/30 text-blue-300"
              >
                {skill}
                <button
                  onClick={() => removeSkill(skill)}
                  className="text-blue-400/60 hover:text-blue-200 ml-0.5"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        )}
        <input
          type="text"
          placeholder="Type skill + Enter"
          onKeyDown={handleSkillKeyDown}
          className="w-full bg-gray-800 border border-white/10 rounded-lg px-3 py-2 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-blue-500/50"
        />
      </div>

      {/* Source */}
      <div>
        <SectionTitle>Source</SectionTitle>
        <div className="space-y-2">
          {SOURCES.map((s) => (
            <label key={s.value} className="flex items-center gap-2 cursor-pointer group">
              <input
                type="radio"
                name="source"
                value={s.value}
                checked={source === s.value}
                onChange={() => setField('source', s.value)}
                className="w-3.5 h-3.5 accent-blue-500 cursor-pointer"
              />
              <span className="text-sm text-gray-300 group-hover:text-white transition-colors">
                {s.label}
              </span>
            </label>
          ))}
        </div>
      </div>
    </div>
  )
}
