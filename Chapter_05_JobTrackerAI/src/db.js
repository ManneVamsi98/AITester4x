import { openDB } from 'idb'
import { STATUS_ORDER } from './constants.js'

const DB_NAME = 'job-tracker'
const DB_VERSION = 1
const STORE = 'jobs'

let dbPromise

function getDB() {
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

export async function getAllJobs() {
  const db = await getDB()
  return db.getAll(STORE)
}

export async function putJob(job) {
  const db = await getDB()
  await db.put(STORE, job)
}

export async function deleteJob(id) {
  const db = await getDB()
  await db.delete(STORE, id)
}

export async function importJobs(jobs) {
  const db = await getDB()
  const tx = db.transaction(STORE, 'readwrite')
  for (const job of jobs) {
    if (job && job.id) {
      // Normalise status to a valid value; default to wishlist.
      const status = STATUS_ORDER.includes(job.status) ? job.status : 'wishlist'
      await tx.store.put({ ...job, status })
    }
  }
  await tx.done
}
