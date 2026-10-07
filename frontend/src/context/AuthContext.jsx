import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import authService from '../services/auth.service'
import toast from 'react-hot-toast'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => authService.getStoredUser())
  const [loading, setLoading] = useState(true)
  const [initializing, setInitializing] = useState(true)

  // Validate stored session on mount
  useEffect(() => {
    const validateSession = async () => {
      if (!authService.isAuthenticated()) {
        setLoading(false)
        setInitializing(false)
        return
      }

      try {
        const currentUser = await authService.getMe()
        setUser(currentUser)
        localStorage.setItem('user', JSON.stringify(currentUser))
      } catch {
        authService.clearTokens()
        setUser(null)
      } finally {
        setLoading(false)
        setInitializing(false)
      }
    }

    validateSession()
  }, [])

  const login = useCallback(async (email, password) => {
    setLoading(true)
    try {
      const data = await authService.login(email, password)
      authService.saveTokens(data.access_token, data.refresh_token, data.user)
      setUser(data.user)
      return { success: true, user: data.user }
    } catch (err) {
      const message = err.response?.data?.detail || 'Login failed'
      return { success: false, error: message }
    } finally {
      setLoading(false)
    }
  }, [])

  const register = useCallback(async (formData) => {
    setLoading(true)
    try {
      const data = await authService.register(formData)
      authService.saveTokens(data.access_token, data.refresh_token, data.user)
      setUser(data.user)
      return { success: true, user: data.user }
    } catch (err) {
      const message = err.response?.data?.detail || 'Registration failed'
      return { success: false, error: message }
    } finally {
      setLoading(false)
    }
  }, [])

  const logout = useCallback(async () => {
    try {
      await authService.logout()
    } finally {
      setUser(null)
      authService.clearTokens()
    }
  }, [])

  const forgotPassword = useCallback(async (email) => {
    try {
      const data = await authService.forgotPassword(email)
      return { success: true, data }
    } catch (err) {
      const message = err.response?.data?.detail || 'Request failed'
      return { success: false, error: message }
    }
  }, [])

  const resetPassword = useCallback(async (token, newPassword) => {
    try {
      await authService.resetPassword(token, newPassword)
      return { success: true }
    } catch (err) {
      const message = err.response?.data?.detail || 'Reset failed'
      return { success: false, error: message }
    }
  }, [])

  const value = {
    user,
    loading,
    initializing,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    forgotPassword,
    resetPassword,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuthContext() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuthContext must be used within AuthProvider')
  }
  return context
}

export default AuthContext
