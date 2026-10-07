import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import toast from 'react-hot-toast'
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline'
import { useAuth } from '../../hooks/useAuth'
import Button from '../../components/ui/Button'
import Input from '../../components/ui/Input'

const CURRENT_YEAR = new Date().getFullYear()

const schema = z.object({
  full_name: z.string().min(2, 'Full name must be at least 2 characters'),
  email: z.string().email('Enter a valid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  confirm_password: z.string(),
  phone: z.string().optional(),
  college: z.string().min(2, 'College name is required'),
  degree: z.string().min(2, 'Degree is required'),
  graduation_year: z.coerce.number().int().min(CURRENT_YEAR - 1).max(CURRENT_YEAR + 8),
  preferred_career: z.string().min(2, 'Preferred career is required'),
}).refine((d) => d.password === d.confirm_password, {
  message: 'Passwords do not match',
  path: ['confirm_password'],
})

const DEGREES = [
  'Bachelor of Science (B.S.)',
  'Bachelor of Arts (B.A.)',
  'Bachelor of Engineering (B.E.)',
  'Bachelor of Technology (B.Tech)',
  'Master of Science (M.S.)',
  'Master of Business Administration (MBA)',
  'Associate Degree',
  'Diploma',
  'Other',
]

const CAREERS = [
  'Software Engineering',
  'Data Science / ML',
  'Product Management',
  'UX/UI Design',
  'Cybersecurity',
  'Cloud Engineering',
  'DevOps / SRE',
  'Business Analysis',
  'Finance / Accounting',
  'Marketing',
  'Healthcare / Medicine',
  'Other',
]

export default function Register() {
  const { register: authRegister } = useAuth()
  const navigate = useNavigate()
  const [showPw, setShowPw] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({ resolver: zodResolver(schema) })

  const onSubmit = async (data) => {
    const { confirm_password, ...payload } = data
    const result = await authRegister(payload)
    if (result.success) {
      toast.success(`Welcome to CareerAI, ${result.user.full_name.split(' ')[0]}! 🎉`)
      navigate('/dashboard')
    } else {
      toast.error(result.error)
    }
  }

  return (
    <div className="w-full max-w-2xl">
      <div className="glass rounded-2xl border border-white/8 p-8">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-white">Create your account</h1>
          <p className="text-gray-400 mt-1 text-sm">Start your AI-powered career journey — free forever</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          {/* Row 1: Name + Email */}
          <div className="grid sm:grid-cols-2 gap-4">
            <Input
              label="Full Name"
              placeholder="Jane Doe"
              required
              error={errors.full_name?.message}
              {...register('full_name')}
            />
            <Input
              label="Email Address"
              type="email"
              placeholder="jane@example.com"
              required
              error={errors.email?.message}
              {...register('email')}
            />
          </div>

          {/* Row 2: Password + Confirm */}
          <div className="grid sm:grid-cols-2 gap-4">
            <div className="relative">
              <Input
                label="Password"
                type={showPw ? 'text' : 'password'}
                placeholder="Min. 8 characters"
                required
                error={errors.password?.message}
                {...register('password')}
              />
              <button type="button" onClick={() => setShowPw(!showPw)}
                className="absolute right-3 top-[34px] text-gray-500 hover:text-gray-300">
                {showPw ? <EyeSlashIcon className="w-4 h-4" /> : <EyeIcon className="w-4 h-4" />}
              </button>
            </div>
            <div className="relative">
              <Input
                label="Confirm Password"
                type={showConfirm ? 'text' : 'password'}
                placeholder="Repeat password"
                required
                error={errors.confirm_password?.message}
                {...register('confirm_password')}
              />
              <button type="button" onClick={() => setShowConfirm(!showConfirm)}
                className="absolute right-3 top-[34px] text-gray-500 hover:text-gray-300">
                {showConfirm ? <EyeSlashIcon className="w-4 h-4" /> : <EyeIcon className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Row 3: College + Phone */}
          <div className="grid sm:grid-cols-2 gap-4">
            <Input
              label="College / University"
              placeholder="State University"
              required
              error={errors.college?.message}
              {...register('college')}
            />
            <Input
              label="Phone (optional)"
              type="tel"
              placeholder="+1 555 000 0000"
              error={errors.phone?.message}
              {...register('phone')}
            />
          </div>

          {/* Row 4: Degree + Graduation Year */}
          <div className="grid sm:grid-cols-2 gap-4">
            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium text-gray-300">
                Degree <span className="text-red-400">*</span>
              </label>
              <select
                className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent hover:border-white/20 transition-all"
                {...register('degree')}
              >
                <option value="" className="bg-gray-900">Select degree…</option>
                {DEGREES.map((d) => <option key={d} value={d} className="bg-gray-900">{d}</option>)}
              </select>
              {errors.degree && <p className="text-xs text-red-400">⚠ {errors.degree.message}</p>}
            </div>
            <Input
              label="Graduation Year"
              type="number"
              placeholder={String(CURRENT_YEAR + 1)}
              required
              error={errors.graduation_year?.message}
              {...register('graduation_year')}
            />
          </div>

          {/* Preferred Career */}
          <div className="flex flex-col gap-1.5">
            <label className="text-sm font-medium text-gray-300">
              Preferred Career <span className="text-red-400">*</span>
            </label>
            <select
              className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent hover:border-white/20 transition-all"
              {...register('preferred_career')}
            >
              <option value="" className="bg-gray-900">Select career goal…</option>
              {CAREERS.map((c) => <option key={c} value={c} className="bg-gray-900">{c}</option>)}
            </select>
            {errors.preferred_career && <p className="text-xs text-red-400">⚠ {errors.preferred_career.message}</p>}
          </div>

          <Button type="submit" variant="primary" size="lg" loading={isSubmitting} disabled={isSubmitting} className="w-full mt-2">
            Create Free Account
          </Button>

          <p className="text-xs text-gray-600 text-center">
            By registering you agree to our{' '}
            <a href="/terms" className="text-gray-400 hover:text-white">Terms of Service</a>
            {' '}and{' '}
            <a href="/privacy" className="text-gray-400 hover:text-white">Privacy Policy</a>.
          </p>
        </form>

        <p className="text-center text-sm text-gray-500 mt-6">
          Already have an account?{' '}
          <Link to="/login" className="text-blue-400 hover:text-blue-300 font-medium transition-colors">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
