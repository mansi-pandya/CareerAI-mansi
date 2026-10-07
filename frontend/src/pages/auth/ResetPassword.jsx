import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import toast from 'react-hot-toast'
import { EyeIcon, EyeSlashIcon, KeyIcon } from '@heroicons/react/24/outline'
import { useAuth } from '../../hooks/useAuth'
import Button from '../../components/ui/Button'
import Input from '../../components/ui/Input'

const schema = z.object({
  new_password: z.string().min(8, 'Password must be at least 8 characters'),
  confirm_password: z.string(),
}).refine((d) => d.new_password === d.confirm_password, {
  message: 'Passwords do not match',
  path: ['confirm_password'],
})

export default function ResetPassword() {
  const { resetPassword } = useAuth()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [showPw, setShowPw] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const token = searchParams.get('token') || ''

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({ resolver: zodResolver(schema) })

  const onSubmit = async (data) => {
    if (!token) {
      toast.error('Invalid or missing reset token')
      return
    }
    const result = await resetPassword(token, data.new_password)
    if (result.success) {
      toast.success('Password reset successfully! Please sign in.')
      navigate('/login')
    } else {
      toast.error(result.error)
    }
  }

  if (!token) {
    return (
      <div className="w-full max-w-md">
        <div className="glass rounded-2xl border border-red-500/20 p-8 text-center">
          <p className="text-red-400 font-medium">Invalid or expired reset link.</p>
          <p className="text-gray-500 text-sm mt-2">Please request a new one.</p>
          <Link to="/forgot-password" className="mt-4 block">
            <Button variant="outline" size="md" className="w-full">Request New Link</Button>
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full max-w-md">
      <div className="glass rounded-2xl border border-white/8 p-8">
        <div className="w-12 h-12 rounded-xl bg-indigo-900/30 border border-indigo-500/20 flex items-center justify-center mb-6">
          <KeyIcon className="w-6 h-6 text-indigo-400" />
        </div>

        <h1 className="text-2xl font-bold text-white mb-2">Set new password</h1>
        <p className="text-gray-400 text-sm mb-7">Choose a strong password for your account.</p>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          <div className="relative">
            <Input
              label="New Password"
              type={showPw ? 'text' : 'password'}
              placeholder="Min. 8 characters"
              required
              error={errors.new_password?.message}
              {...register('new_password')}
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
              placeholder="Repeat new password"
              required
              error={errors.confirm_password?.message}
              {...register('confirm_password')}
            />
            <button type="button" onClick={() => setShowConfirm(!showConfirm)}
              className="absolute right-3 top-[34px] text-gray-500 hover:text-gray-300">
              {showConfirm ? <EyeSlashIcon className="w-4 h-4" /> : <EyeIcon className="w-4 h-4" />}
            </button>
          </div>

          <Button type="submit" variant="primary" size="lg" loading={isSubmitting} disabled={isSubmitting} className="w-full">
            Reset Password
          </Button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-6">
          <Link to="/login" className="text-blue-400 hover:text-blue-300 font-medium transition-colors">Back to Sign In</Link>
        </p>
      </div>
    </div>
  )
}
