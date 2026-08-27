import { openDB } from 'idb'
import { supabase, isSupabaseConfigured } from './supabase.js'
import { STATUS_ORDER } from './constants.js'

const DB_NAME = 'job-tracker'
const DB_VERSION = 1
const STORE = 'jobs'
const TABLE = 'jobs'

let dbPromise

function getLocalDB() {
  if (!dbPromise) {
    dbPromise = openDB(DB_NAME, DB_VERSION, {
      upgrade(db) {
        if (!db.objectStoreNames.contains(STORE)) {
          const store = db.createObjectStore(STORE, { keyPath: 'id' })
          store.createIndex('status', 'status')
          store.createIndex('dateApplied', 'dateApplied')
        }
      },
    })
  }
  return dbPromise
}

// --- Local IndexedDB mirror (offline fallback + migration source) ---

async function getAllLocal() {
  const db = await getLocalDB()
  return db.getAll(STORE)
}

async function putLocal(job) {
  const db = await getLocalDB()
  await db.put(STORE, job)
}

async function deleteLocal(id) {
  const db = await getLocalDB()
  await db.delete(STORE, id)
}

// --- Cloud (Supabase) ---

function userId() {
  return supabase.auth.getUser().then(({ data }) => data.user?.id || null)
}

export async function getAllJobs() {
  if (!isSupabaseConfigured || !supabase) return getAllLocal()
  const { data, error } = await supabase.from(TABLE).select('*').order('dateApplied', { ascending: true })
  if (error) {
    // Offline or RLS failure — fall back to the local mirror.
    return getAllLocal()
  }
  return data || []
}

export async function putJob(job) {
  putLocal(job).catch(() => {}) // best-effort mirror
  if (!isSupabaseConfigured || !supabase) return
  const uid = await userId()
  if (!uid) return
  const { error } = await supabase.from(TABLE).upsert({ ...job, user_id: uid }, { onConflict: 'id' })
  if (error) console.error('Failed to save job to cloud:', error.message)
}

export async function deleteJob(id) {
  deleteLocal(id).catch(() => {})
  if (!isSupabaseConfigured || !supabase) return
  const { error } = await supabase.from(TABLE).delete().eq('id', id)
  if (error) console.error('Failed to delete job from cloud:', error.message)
}

export async function importJobs(jobs) {
  // Keep local mirror fresh regardless.
  const db = await getLocalDB()
  const tx = db.transaction(STORE, 'readwrite')
  for (const job of jobs) {
    if (job && job.id) {
      const status = STATUS_ORDER.includes(job.status) ? job.status : 'wishlist'
      await tx.store.put({ ...job, status })
    }
  }
  await tx.done

  if (!isSupabaseConfigured || !supabase) return
  const uid = await userId()
  if (!uid) return
  const rows = jobs
    .filter((j) => j && j.id)
    .map((j) => ({
      ...j,
      status: STATUS_ORDER.includes(j.status) ? j.status : 'wishlist',
      user_id: uid,
    }))
  const { error } = await supabase.from(TABLE).upsert(rows, { onConflict: 'id' })
  if (error) console.error('Failed to import jobs to cloud:', error.message)
}

// One-time upload of existing local IndexedDB jobs into the cloud.
export async function migrateLocalToCloud() {
  if (!isSupabaseConfigured || !supabase) return false
  const local = await getAllLocal()
  if (!local.length) return false

  const uid = await userId()
  if (!uid) return false

  const { data: existing } = await supabase.from(TABLE).select('id').limit(1)
  if (existing && existing.length) return false // cloud already has data

  const rows = local.map((j) => ({ ...j, user_id: uid }))
  const { error } = await supabase.from(TABLE).upsert(rows, { onConflict: 'id' })
  if (error) {
    console.error('Migration failed:', error.message)
    return false
  }
  return true
}
