import { createContext, useContext, useEffect, useState } from 'react'
import { api } from './api'
import type { AuthUser } from './types'

interface AuthContextValue {
  user: AuthUser | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, displayName: string) => Promise<void>
  logout: () => Promise<void>
  refresh: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(true)

  async function refresh() {
    try {
      const currentUser = await api.get<AuthUser>('/auth/me')
      setUser(currentUser)
    } catch {
      setUser(null)
    }
  }

  async function login(email: string, password: string) {
    const currentUser = await api.post<AuthUser>('/auth/login', { email, password })
    setUser(currentUser)
  }

  async function register(email: string, password: string, displayName: string) {
    const currentUser = await api.post<AuthUser>('/auth/register', {
      email,
      password,
      display_name: displayName || null,
    })
    setUser(currentUser)
  }

  async function logout() {
    await api.post<void>('/auth/logout', {})
    setUser(null)
  }

  useEffect(() => {
    refresh().finally(() => setLoading(false))
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, refresh }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const value = useContext(AuthContext)
  if (!value) {
    throw new Error('useAuth must be used inside AuthProvider')
  }
  return value
}
