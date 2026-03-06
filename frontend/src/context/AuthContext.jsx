// frontend/src/context/AuthContext.jsx
// Global authentication state using React Context.
// Wraps the entire app so ANY component can access the current user
// without passing props down manually.

import { createContext, useContext, useEffect, useState } from 'react'
import { supabase } from '../api/supabaseClient'

// Create the context object
const AuthContext = createContext({})

// Custom hook — components call useAuth() to get user/session
export const useAuth = () => useContext(AuthContext)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [session, setSession] = useState(null)
  const [loading, setLoading] = useState(true)  // true while we check session

  useEffect(() => {
    // On app load, check if user already has an active session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      setUser(session?.user ?? null)
      setLoading(false)
    })

    // Listen for login/logout events and update state automatically
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setSession(session)
        setUser(session?.user ?? null)
        setLoading(false)
      }
    )

    // Cleanup listener when component unmounts
    return () => subscription.unsubscribe()
  }, [])

  // Sign up with email + password
  const signUp = async (email, password) => {
    const { data, error } = await supabase.auth.signUp({ email, password })
    return { data, error }
  }

  // Login with email + password
  const signIn = async (email, password) => {
    const { data, error } = await supabase.auth.signInWithPassword({ 
      email, 
      password 
    })
    return { data, error }
  }

  // Logout
  const signOut = async () => {
    await supabase.auth.signOut()
  }

  // Get the JWT token for Flask API calls
  const getToken = async () => {
    const { data: { session } } = await supabase.auth.getSession()
    return session?.access_token
  }

  const value = { user, session, loading, signUp, signIn, signOut, getToken }

  // Don't render children until we know auth state (prevents flash)
  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  )
}