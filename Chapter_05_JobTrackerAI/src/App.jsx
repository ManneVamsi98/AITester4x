import { useEffect, useMemo, useRef, useState } from 'react'
import {
  DndContext,
  DragOverlay,
  PointerSensor,
  closestCorners,
  useSensor,
  useSensors,
} from '@dnd-kit/core'
import { arrayMove, sortableKeyboardCoordinates } from '@dnd-kit/sortable'
import { KeyboardSensor } from '@dnd-kit/core'
import KanbanColumn from './components/KanbanColumn.jsx'
import JobForm from './components/JobForm.jsx'
import Modal from './components/Modal.jsx'
import JobCard from './components/JobCard.jsx'
import { STATUSES, STATUS_ORDER } from './constants.js'
import { getAllJobs, putJob, deleteJob, importJobs } from './db.js'
import { exportJSON, readJSONFile } from './utils/io.js'

function uid() {
  return (crypto.randomUUID ? crypto.randomUUID() : 'id-' + Date.now() + '-' + Math.random().toString(16).slice(2))
}

export default function App() {
  const [jobs, setJobs] = useState([])
  const [loaded, setLoaded] = useState(false)
  const [search, setSearch] = useState('')
  const [modal, setModal] = useState(null) // { mode: 'add'|'edit', status?, job? }
  const [confirmDelete, setConfirmDelete] = useState(null)
  const [activeId, setActiveId] = useState(null)
  const [dark, setDark] = useState(() => window.matchMedia?.('(prefers-color-scheme: dark)').matches ?? false)
  const [overColumn, setOverColumn] = useState(null)
  const fileRef = useRef(null)

  useEffect(() => {
    getAllJobs().then((rows) => {
      setJobs(rows)
      setLoaded(true)
    })
  }, [])

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
  }, [dark])

  const resumeNames = useMemo(
    () => [...new Set(jobs.map((j) => j.resume).filter(Boolean))].sort(),
    [jobs],
  )

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase()
    if (!q) return jobs
    return jobs.filter(
      (j) => j.company.toLowerCase().includes(q) || j.role.toLowerCase().includes(q),
    )
  }, [jobs, search])

  const columns = useMemo(() => {
    const map = Object.fromEntries(STATUS_ORDER.map((s) => [s, []]))
    for (const j of filtered) map[j.status]?.push(j)
    return map
  }, [filtered])

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 6 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  )

  function handleDragStart({ active }) {
    setActiveId(active.id)
  }

  function handleDragOver({ over }) {
    if (over) setOverColumn(over.data.current?.sortable?.containerId ?? over.id)
  }

  function handleDragEnd({ active, over }) {
    setActiveId(null)
    setOverColumn(null)
    if (!over) return

    const activeJob = jobs.find((j) => j.id === active.id)
    if (!activeJob) return

    const fromId = activeJob.status
    const toId = STATUS_ORDER.includes(over.id)
      ? over.id
      : (over.data.current?.sortable?.containerId ?? fromId)

    if (fromId === toId) {
      // Reorder within the same column. Use the (possibly filtered) column to
      // compute the new order, then merge back without dropping any jobs.
      const col = columns[fromId]
      const oldIndex = col.findIndex((j) => j.id === active.id)
      const overIndex = col.findIndex((j) => j.id === over.id)
      if (oldIndex === -1 || overIndex === -1 || oldIndex === overIndex) return
      const reordered = arrayMove(col, oldIndex, overIndex)
      const order = new Map(reordered.map((j, i) => [j.id, i]))
      setJobs((prev) => {
        const inCol = prev
          .filter((j) => j.status === fromId)
          .sort((a, b) => {
            const ia = order.has(a.id) ? order.get(a.id) : Infinity
            const ib = order.has(b.id) ? order.get(b.id) : Infinity
            return ia - ib
          })
        return [...prev.filter((j) => j.status !== fromId), ...inCol]
      })
      return
    }

    // Move to a different column.
    const updated = { ...activeJob, status: toId }
    setJobs((prev) => prev.map((j) => (j.id === updated.id ? updated : j)))
    putJob(updated)
  }

  function handleSave(form) {
    if (modal.mode === 'edit' && modal.job) {
      const updated = { ...modal.job, ...form }
      setJobs((prev) => prev.map((j) => (j.id === updated.id ? updated : j)))
      putJob(updated)
    } else {
      const job = { id: uid(), ...form }
      setJobs((prev) => [...prev, job])
      putJob(job)
    }
    setModal(null)
  }

  function handleDelete() {
    if (!confirmDelete) return
    setJobs((prev) => prev.filter((j) => j.id !== confirmDelete))
    deleteJob(confirmDelete)
    setConfirmDelete(null)
  }

  function handleExport() {
    exportJSON(jobs)
  }

  async function handleImport(e) {
    const file = e.target.files?.[0]
    e.target.value = ''
    if (!file) return
    try {
      const data = await readJSONFile(file)
      await importJobs(data)
      setJobs(await getAllJobs())
    } catch (err) {
      alert(err.message || 'Import failed')
    }
  }

  const activeJob = jobs.find((j) => j.id === activeId)

  if (!loaded) {
    return (
      <div className="flex h-full items-center justify-center text-sm text-slate-500 dark:text-slate-400">
        Loading…
      </div>
    )
  }

  return (
    <div className="flex h-full flex-col bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
      {/* Header */}
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 bg-white px-4 py-3 dark:border-slate-800 dark:bg-slate-900">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 text-sm font-bold text-white">JT</div>
          <div>
            <h1 className="text-base font-bold leading-tight">Job Tracker</h1>
            <p className="text-xs text-slate-400 dark:text-slate-500">Local-first · {jobs.length} job{jobs.length === 1 ? '' : 's'}</p>
          </div>
        </div>

        <div className="flex flex-1 items-center gap-2 sm:max-w-md">
          <div className="relative w-full">
            <svg viewBox="0 0 24 24" className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="7" />
              <path d="m21 21-4.3-4.3" />
            </svg>
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by company or role…"
              className="w-full rounded-md border border-slate-300 bg-white py-2 pl-9 pr-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-800"
            />
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button onClick={() => fileRef.current?.click()} title="Import JSON backup" className="rounded-md border border-slate-300 px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800">
            Import
          </button>
          <button onClick={handleExport} title="Export all jobs as JSON" className="rounded-md border border-slate-300 px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800">
            Export
          </button>
          <button
            onClick={() => setDark((d) => !d)}
            title="Toggle dark mode"
            className="rounded-md border border-slate-300 p-2 text-slate-600 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            {dark ? (
              <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="4" />
                <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
              </svg>
            ) : (
              <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />
              </svg>
            )}
          </button>
          <button onClick={() => setModal({ mode: 'add', status: 'wishlist' })} className="rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white hover:bg-blue-700">
            + Add job
          </button>
        </div>
      </header>

      {/* Board */}
      <main className="flex flex-1 gap-4 overflow-x-auto overflow-y-hidden p-4">
        <DndContext
          sensors={sensors}
          collisionDetection={closestCorners}
          onDragStart={handleDragStart}
          onDragOver={handleDragOver}
          onDragEnd={handleDragEnd}
          onDragCancel={() => {
            setActiveId(null)
            setOverColumn(null)
          }}
        >
          {STATUSES.map((s) => (
            <KanbanColumn
              key={s.id}
              status={s.id}
              label={s.label}
              jobs={columns[s.id]}
              onEdit={(job) => setModal({ mode: 'edit', job })}
              onAdd={(status) => setModal({ mode: 'add', status })}
              isOver={overColumn === s.id}
            />
          ))}
          <DragOverlay>
            {activeJob ? <div className="w-72"><JobCard job={activeJob} onEdit={() => {}} /></div> : null}
          </DragOverlay>
        </DndContext>
      </main>

      <input ref={fileRef} type="file" accept="application/json" className="hidden" onChange={handleImport} />

      {/* Add / edit modal */}
      {modal && (
        <Modal title={modal.mode === 'edit' ? 'Edit job' : 'Add job'} onClose={() => setModal(null)}>
          <JobForm
            initial={modal.mode === 'edit' ? { ...modal.job, status: modal.job.status } : { status: modal.status }}
            resumeNames={resumeNames}
            onSubmit={handleSave}
            onCancel={() => setModal(null)}
            onDelete={modal.mode === 'edit' ? () => setConfirmDelete(modal.job.id) : null}
          />
        </Modal>
      )}

      {/* Delete confirmation */}
      {confirmDelete && (
        <Modal title="Delete job?" onClose={() => setConfirmDelete(null)}>
          <p className="text-sm text-slate-600 dark:text-slate-300">
            Are you sure you want to delete this job? This cannot be undone.
          </p>
          <div className="mt-5 flex justify-end gap-2">
            <button onClick={() => setConfirmDelete(null)} className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-700">
              Cancel
            </button>
            <button onClick={handleDelete} className="rounded-md bg-rose-600 px-4 py-2 text-sm font-medium text-white hover:bg-rose-700">
              Delete
            </button>
          </div>
        </Modal>
      )}
    </div>
  )
}
