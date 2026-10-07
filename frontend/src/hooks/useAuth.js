import { useAuthContext } from '../context/AuthContext'

// Convenience re-export so components can import from a single place
export function useAuth() {
  return useAuthContext()
}

export default useAuth
