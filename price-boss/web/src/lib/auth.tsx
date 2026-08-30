import { createContext, useContext, useMemo, useState, type ReactNode } from 'react'
import { can, clearUser, loadUser, saveUser, type User } from '../lib/api'

type AuthCtx = {
  user: User | null
  setUser: (u: User | null) => void
  logout: () => void
  can: (perm: string) => boolean
}

const Ctx = createContext<AuthCtx | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUserState] = useState<User | null>(() => loadUser())
  const value = useMemo<AuthCtx>(
    () => ({
      user,
      setUser: (u) => {
        if (u) saveUser(u)
        else clearUser()
        setUserState(u)
      },
      logout: () => {
        clearUser()
        setUserState(null)
      },
      can: (perm) => can(user, perm),
    }),
    [user],
  )
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export function useAuth() {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useAuth outside provider')
  return ctx
}
