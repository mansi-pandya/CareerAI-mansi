import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import toast from 'react-hot-toast'
import {
  UserCircleIcon,
  PencilSquareIcon,
  CheckIcon,
  XMarkIcon,
  PlusIcon,
  TrashIcon,
  LinkIcon,
} from '@heroicons/react/24/outline'
import api from '../../services/api'
import { useAuth } from '../../hooks/useAuth'
import Card from '../../components/ui/Card'
import Button from '../../components/ui/Button'
import Input from '../../components/ui/Input'
import Badge from '../../components/ui/Badge'
import ProgressBar from '../../components/ui/ProgressBar'

const profileSchema = z.object({
  college: z.string().min(2).optional().or(z.literal('')),
  degree: z.string().min(2).optional().or(z.literal('')),
  major: z.string().optional().or(z.literal('')),
  graduation_year: z.coerce.number().int().min(1990).max(2040).optional().nullable(),
  gpa: z.coerce.number().min(0).max(10).optional().nullable(),
  bio: z.string().max(500).optional().or(z.literal('')),
  linkedin_url: z.string().url('Must be a valid URL').optional().or(z.literal('')),
  github_url: z.string().url('Must be a valid URL').optional().or(z.literal('')),
  portfolio_url: z.string().url('Must be a valid URL').optional().or(z.literal('')),
  preferred_career: z.string().optional().or(z.literal('')),
  location: z.string().optional().or(z.literal('')),
})

const skillSchema = z.object({
  skill_name: z.string().min(1, 'Skill name required'),
  proficiency: z.enum(['beginner', 'intermediate', 'advanced', 'expert']),
})

const PROFICIENCY_COLORS = {
  beginner: 'default',
  intermediate: 'blue',
  advanced: 'purple',
  expert: 'green',
}

function ProfileCompletenessBar({ profile }) {
  const fields = [
    profile?.college,
    profile?.degree,
    profile?.graduation_year,
    profile?.preferred_career,
    profile?.bio,
    profile?.linkedin_url || profile?.github_url,
    profile?.skills?.length > 0,
    profile?.education?.length > 0,
  ]
  const filled = fields.filter(Boolean).length
  const pct = Math.round((filled / fields.length) * 100)

  return (
    <Card className="mb-6">
      <Card.Body>
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-medium text-white">Profile Completeness</span>
          <span className="text-sm font-bold text-blue-400">{pct}%</span>
        </div>
        <ProgressBar value={pct} color="blue" showValue={false} size="md" />
        {pct < 100 && (
          <p className="text-xs text-gray-500 mt-2">
            Complete your profile to unlock personalized career insights and better job matches.
          </p>
        )}
      </Card.Body>
    </Card>
  )
}

export default function Profile() {
  const { user } = useAuth()
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(false)
  const [addingSkill, setAddingSkill] = useState(false)

  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm({
    resolver: zodResolver(profileSchema),
  })

  const { register: regSkill, handleSubmit: handleSkill, reset: resetSkill, formState: { errors: skillErrors, isSubmitting: skillSubmitting } } = useForm({
    resolver: zodResolver(skillSchema),
    defaultValues: { proficiency: 'beginner' },
  })

  const fetchProfile = async () => {
    try {
      const res = await api.get('/profile/')
      setProfile(res.data)
      reset({
        college: res.data.college || '',
        degree: res.data.degree || '',
        major: res.data.major || '',
        graduation_year: res.data.graduation_year || '',
        gpa: res.data.gpa || '',
        bio: res.data.bio || '',
        linkedin_url: res.data.linkedin_url || '',
        github_url: res.data.github_url || '',
        portfolio_url: res.data.portfolio_url || '',
        preferred_career: res.data.preferred_career || '',
        location: res.data.location || '',
      })
    } catch {
      toast.error('Failed to load profile')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchProfile() }, [])

  const onSave = async (data) => {
    try {
      const res = await api.put('/profile/', data)
      setProfile(res.data)
      setEditing(false)
      toast.success('Profile updated!')
    } catch {
      toast.error('Failed to save profile')
    }
  }

  const onAddSkill = async (data) => {
    try {
      await api.post('/profile/skills', data)
      await fetchProfile()
      setAddingSkill(false)
      resetSkill()
      toast.success('Skill added!')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to add skill')
    }
  }

  const removeSkill = async (skillId) => {
    try {
      await api.delete(`/profile/skills/${skillId}`)
      setProfile(prev => ({ ...prev, skills: prev.skills.filter(s => s.id !== skillId) }))
      toast.success('Skill removed')
    } catch {
      toast.error('Failed to remove skill')
    }
  }

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[400px]">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-4xl space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">My Profile</h1>
        {!editing && (
          <Button variant="outline" size="sm" onClick={() => setEditing(true)}>
            <PencilSquareIcon className="w-4 h-4" />
            Edit Profile
          </Button>
        )}
      </div>

      <ProfileCompletenessBar profile={profile} />

      {/* Basic info */}
      <Card>
        <Card.Header>
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center">
              <UserCircleIcon className="w-7 h-7 text-white" />
            </div>
            <div>
              <h2 className="font-semibold text-white">{user?.full_name}</h2>
              <p className="text-sm text-gray-400">{user?.email}</p>
            </div>
          </div>
        </Card.Header>
        <Card.Body>
          {editing ? (
            <form onSubmit={handleSubmit(onSave)} className="space-y-5">
              <div className="grid sm:grid-cols-2 gap-4">
                <Input label="College / University" placeholder="State University" error={errors.college?.message} {...register('college')} />
                <Input label="Degree" placeholder="B.S. Computer Science" error={errors.degree?.message} {...register('degree')} />
                <Input label="Major" placeholder="Computer Science" error={errors.major?.message} {...register('major')} />
                <Input label="Graduation Year" type="number" placeholder="2025" error={errors.graduation_year?.message} {...register('graduation_year')} />
                <Input label="GPA" type="number" step="0.01" placeholder="3.8" error={errors.gpa?.message} {...register('gpa')} />
                <Input label="Location" placeholder="New York, NY" error={errors.location?.message} {...register('location')} />
                <Input label="Preferred Career" placeholder="Software Engineer" error={errors.preferred_career?.message} {...register('preferred_career')} />
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-medium text-gray-300">Bio</label>
                <textarea
                  rows={3}
                  placeholder="Tell us about yourself..."
                  className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  {...register('bio')}
                />
                {errors.bio && <p className="text-xs text-red-400">⚠ {errors.bio.message}</p>}
              </div>

              <div className="grid sm:grid-cols-3 gap-4">
                <Input label="LinkedIn URL" placeholder="https://linkedin.com/in/..." error={errors.linkedin_url?.message} {...register('linkedin_url')} />
                <Input label="GitHub URL" placeholder="https://github.com/..." error={errors.github_url?.message} {...register('github_url')} />
                <Input label="Portfolio URL" placeholder="https://yoursite.com" error={errors.portfolio_url?.message} {...register('portfolio_url')} />
              </div>

              <div className="flex gap-3 justify-end">
                <Button type="button" variant="ghost" size="sm" onClick={() => setEditing(false)}>
                  <XMarkIcon className="w-4 h-4" /> Cancel
                </Button>
                <Button type="submit" variant="primary" size="sm" loading={isSubmitting} disabled={isSubmitting}>
                  <CheckIcon className="w-4 h-4" /> Save Changes
                </Button>
              </div>
            </form>
          ) : (
            <div className="grid sm:grid-cols-2 gap-x-8 gap-y-4 text-sm">
              {[
                ['College', profile?.college],
                ['Degree', profile?.degree],
                ['Major', profile?.major],
                ['Graduation Year', profile?.graduation_year],
                ['GPA', profile?.gpa],
                ['Location', profile?.location],
                ['Preferred Career', profile?.preferred_career],
              ].map(([label, val]) => (
                <div key={label}>
                  <span className="text-gray-500">{label}</span>
                  <p className="text-white mt-0.5">{val || <span className="text-gray-600 italic">Not set</span>}</p>
                </div>
              ))}
              {profile?.bio && (
                <div className="sm:col-span-2">
                  <span className="text-gray-500">Bio</span>
                  <p className="text-white mt-0.5">{profile.bio}</p>
                </div>
              )}
              {/* Links */}
              <div className="sm:col-span-2 flex flex-wrap gap-3 mt-2">
                {profile?.linkedin_url && (
                  <a href={profile.linkedin_url} target="_blank" rel="noreferrer" className="flex items-center gap-1.5 text-blue-400 hover:text-blue-300 text-sm">
                    <LinkIcon className="w-4 h-4" /> LinkedIn
                  </a>
                )}
                {profile?.github_url && (
                  <a href={profile.github_url} target="_blank" rel="noreferrer" className="flex items-center gap-1.5 text-blue-400 hover:text-blue-300 text-sm">
                    <LinkIcon className="w-4 h-4" /> GitHub
                  </a>
                )}
                {profile?.portfolio_url && (
                  <a href={profile.portfolio_url} target="_blank" rel="noreferrer" className="flex items-center gap-1.5 text-blue-400 hover:text-blue-300 text-sm">
                    <LinkIcon className="w-4 h-4" /> Portfolio
                  </a>
                )}
              </div>
            </div>
          )}
        </Card.Body>
      </Card>

      {/* Skills */}
      <Card>
        <Card.Header>
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-white">Skills</h3>
            <Button variant="outline" size="sm" onClick={() => setAddingSkill(!addingSkill)}>
              <PlusIcon className="w-4 h-4" />
              Add Skill
            </Button>
          </div>
        </Card.Header>
        <Card.Body>
          {addingSkill && (
            <form onSubmit={handleSkill(onAddSkill)} className="flex flex-wrap gap-3 mb-5 p-4 bg-white/3 rounded-xl border border-white/8">
              <div className="flex-1 min-w-[160px]">
                <Input placeholder="Skill name (e.g. Python)" error={skillErrors.skill_name?.message} {...regSkill('skill_name')} />
              </div>
              <div className="flex flex-col gap-1.5">
                <select className="px-3 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" {...regSkill('proficiency')}>
                  <option value="beginner" className="bg-gray-900">Beginner</option>
                  <option value="intermediate" className="bg-gray-900">Intermediate</option>
                  <option value="advanced" className="bg-gray-900">Advanced</option>
                  <option value="expert" className="bg-gray-900">Expert</option>
                </select>
              </div>
              <div className="flex gap-2 items-start pt-0.5">
                <Button type="submit" variant="primary" size="sm" loading={skillSubmitting}>Add</Button>
                <Button type="button" variant="ghost" size="sm" onClick={() => setAddingSkill(false)}>Cancel</Button>
              </div>
            </form>
          )}

          {profile?.skills?.length ? (
            <div className="flex flex-wrap gap-2">
              {profile.skills.map((s) => (
                <div key={s.id} className="flex items-center gap-2 bg-white/4 border border-white/8 rounded-lg px-3 py-1.5 group">
                  <span className="text-sm text-white">{s.skill.name}</span>
                  <Badge variant={PROFICIENCY_COLORS[s.proficiency] || 'default'} className="text-xs">
                    {s.proficiency}
                  </Badge>
                  <button
                    onClick={() => removeSkill(s.id)}
                    className="w-4 h-4 text-gray-600 hover:text-red-400 transition-colors opacity-0 group-hover:opacity-100"
                  >
                    <XMarkIcon className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-sm">No skills added yet. Click "Add Skill" to get started.</p>
          )}
        </Card.Body>
      </Card>

      {/* Career Preferences */}
      {profile?.career_preferences?.length > 0 && (
        <Card>
          <Card.Header>
            <h3 className="font-semibold text-white">Career Preferences</h3>
          </Card.Header>
          <Card.Body>
            <div className="flex flex-wrap gap-2">
              {profile.career_preferences.map((p) => (
                <div key={p.id} className="flex items-center gap-2 bg-white/4 border border-white/8 rounded-lg px-3 py-1.5">
                  <span className="text-sm text-white">{p.career_title}</span>
                  {p.is_primary && <Badge variant="blue">Primary</Badge>}
                </div>
              ))}
            </div>
          </Card.Body>
        </Card>
      )}
    </div>
  )
}
