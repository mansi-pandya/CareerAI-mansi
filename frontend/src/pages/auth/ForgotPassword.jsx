import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import toast from 'react-hot-toast'
import { EnvelopeIcon, CheckCircleIcon } from '@heroicons/react/24/outline'
import { useAuth } from '../../hooks/useAuth'
import Button from '../../components/ui/Button'
import Input from '../../components/ui/Input'

const schema = z.object({
  email: z.string().email('Enter a valid email address'),
})

export default function ForgotPassword() {
  const { forgotPassword } = useAuth()
  const [sent, setSent] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({ resolver: zodResolver(schema) })

  const onSubmit = async (data) => {
    const result = await forgotPassword(data.email)
    if (result.success) {
      setSent(true)
    } else {
      toast.error(result.error)
    }
  }

  if (sent) {
    return (
      <div className="w-full max-w-md">
        <div className="glass rounded-2xl border border-white/8 p-8 text-center">
          <div className="w-16 h-16 rounded-full bg-emerald-900/30 border border-emerald-500/30 flex items-center justify-center mx-auto mb-5">
            <CheckCircleIcon className="w-8 h-8 text-emerald-400" />
          </div>
          <h1 className="text-2xl font-bold text-white mb-2">Check your email</h1>
          <p className="text-gray-400 text-sm mb-6">
            If that email is registered, a password reset link has been sent. Check your inbox (and spam folder).
          </p>
          <Link to="/login">
            <Button variant="outline" size="md" className="w-full">Back to Sign In</Button>
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full max-w-md">
      <div className="glass rounded-2xl border border-white/8 p-8">
        <div className="w-12 h-12 rounded-xl bg-blue-900/30 border border-blue-500/20 flex items-center justify-center mb-6">
          <EnvelopeIcon className="w-6 h-6 text-blue-400" />
        </div>

        <h1 className="text-2xl font-bold text-white mb-2">Forgot password?</h1>
        <p className="text-gray-400 text-sm mb-7">
          Enter the email address linked to your account and we'll send you a reset link.
        </p>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          <Input
            label="Email address"
            type="email"
            placeholder="you@example.com"
            required
            error={errors.email?.message}
            {...register('email')}
          />

          <Button type="submit" variant="primary" size="lg" loading={isSubmitting} disabled={isSubmitting} className="w-full">
            Send Reset Link
          </Button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-6">
          Remember your password?{' '}
          <Link to="/login" className="text-blue-400 hover:text-blue-300 font-medium transition-colors">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
