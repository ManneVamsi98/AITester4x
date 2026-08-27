import { supabase, isSupabaseConfigured } from './supabase.js'

export async function signIn(email, password) {
  const { error } = await supabase.auth.signInWithPassword({ email, password })
  if (error) throw new Error(error.message)
}

export async function signUp(email, password) {
  const { error } = await supabase.auth.signUp({ email, password })
  if (error) throw new Error(error.message)
}

export async function signOut() {
  const { error } = await supabase.auth.signOut()
  if (error) throw new Error(error.message)
}

export function getSession() {
  return supabase.auth.getSession()
}

export function onAuthStateChange(cb) {
  const { data } = supabase.auth.onAuthStateChange((_event, session) => cb(session))
  return data.subscription.unsubscribe
}

export { isSupabaseConfigured }
