// frontend/src/context/AuthContext.jsx
import { createContext, useContext, useEffect, useState } from 'react'
import { supabase } from '../api/supabaseClient'

const AuthContext = createContext({})
export const useAuth = () => useContext(AuthContext)

export function AuthProvider({ children }) {
  const [user,    setUser]    = useState(null)
  const [session, setSession] = useState(null)
  const [role,    setRole]    = useState(null)
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)

  // Fetch role + profile from profiles table
  const fetchProfile = async (userId) => {
    if (!userId) { setRole(null); setProfile(null); return }
    try {
      const { data } = await supabase
        .from('profiles')
        .select('role, full_name, email')
        .eq('id', userId)
        .single()
      setRole(data?.role ?? 'responder')
      setProfile(data ?? null)
    } catch {
      setRole('responder')
    }
  }

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      setUser(session?.user ?? null)
      fetchProfile(session?.user?.id)
      setLoading(false)
    })

    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setSession(session)
        setUser(session?.user ?? null)
        fetchProfile(session?.user?.id)
        setLoading(false)
      }
    )

    return () => subscription.unsubscribe()
  }, [])

  // signUp passes full_name + role into user metadata
  // The DB trigger handle_new_user() reads these and inserts into profiles
  const signUp = async (email, password, fullName, userRole) => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name: fullName,
          role:      userRole,
        }
      }
    })
    return { data, error }
  }

  const signIn = async (email, password) => {
    const { data, error } = await supabase.auth.signInWithPassword({ email, password })
    return { data, error }
  }

  const signOut = async () => {
    await supabase.auth.signOut()
    setRole(null)
    setProfile(null)
  }

  const getToken = async () => {
    const { data: { session } } = await supabase.auth.getSession()
    return session?.access_token
  }

  const isAdmin     = role === 'admin'
  const isResponder = role !== null && role !== 'admin'

  const value = {
    user, session, loading,
    role, profile,
    isAdmin, isResponder,
    signUp, signIn, signOut, getToken,
  }

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  )
}