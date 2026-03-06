// frontend/src/api/supabaseClient.js
// Creates ONE shared Supabase client used across the whole frontend.
// Import this wherever you need auth or direct DB reads.

import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseAnonKey)