import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { STATUS_ACCENT } from '../constants.js'

function daysSince(dateStr) {
  if (!dateStr) return null
  const d = new Date(dateStr + 'T00:00:00')
  if (isNaN(d)) return null
  const diff = Date.now() - d.getTime()
  const days = Math.floor(diff / 86400000)
  if (days < 0) return 'in future'
  if (days === 0) return 'today'
  if (days === 1) return '1d ago'
  return `${days}d ago`
}

function formatDate(dateStr) {
  if (!dateStr) return null
  const d = new Date(dateStr + 'T00:00:00')
  if (isNaN(d)) return null
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}

function LinkedInIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="currentColor" aria-hidden="true">
      <path d="M20.45 20.45h-3.55v-5.57c0-1.33-.03-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.47-.9 1.63-1.85 3.36-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12zM7.12 20.45H3.56V9h3.56v11.45z" />
    </svg>
  )
}

export default function JobCard({ job, onEdit }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: job.id })
  const accent = STATUS_ACCENT[job.status] || STATUS_ACCENT.wishlist

  return (
    <div
      ref={setNodeRef}
      style={{ transform: CSS.Transform.toString(transform), transition }}
      {...attributes}
      {...listeners}
      className={`group cursor-grab rounded-md border border-slate-200 border-l-4 ${accent.border} bg-white p-3 shadow-sm transition hover:shadow dark:border-slate-700 dark:bg-slate-800 ${
        isDragging ? 'z-10 opacity-60 shadow-lg ring-2 ring-blue-500' : ''
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <h3 className="truncate text-sm font-semibold text-slate-900 dark:text-slate-100">{job.company}</h3>
          <p className="truncate text-xs text-slate-500 dark:text-slate-400">{job.role}</p>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation()
            onEdit(job)
          }}
          className="shrink-0 rounded p-1 text-slate-400 opacity-0 transition hover:bg-slate-100 hover:text-slate-600 group-hover:opacity-100 dark:hover:bg-slate-700 dark:hover:text-slate-200"
          title="Edit"
          onPointerDown={(e) => e.stopPropagation()}
        >
          <svg viewBox="0 0 24 24" className="h-3.5 w-3.5" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 20h9M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
          </svg>
        </button>
      </div>

      <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-slate-500 dark:text-slate-400">
        {job.resume && (
          <span className="inline-flex items-center gap-1 rounded bg-slate-100 px-1.5 py-0.5 font-medium text-slate-600 dark:bg-slate-700 dark:text-slate-300">
            <svg viewBox="0 0 24 24" className="h-3 w-3" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6zM14 2v6h6M9 15h6M9 18h6" />
            </svg>
            {job.resume}
          </span>
        )}
        <span className="inline-flex flex-col leading-tight">
          <span className="inline-flex items-center gap-1">
            <svg viewBox="0 0 24 24" className="h-3 w-3" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="4" width="18" height="18" rx="2" />
              <path d="M16 2v4M8 2v4M3 10h18" />
            </svg>
            {formatDate(job.dateApplied) || '—'}
          </span>
          {daysSince(job.dateApplied) && (
            <span className="pl-4 text-[10px] text-slate-400 dark:text-slate-500">({daysSince(job.dateApplied)})</span>
          )}
        </span>
        {job.salary && <span className="truncate">{job.salary}</span>}
      </div>

      <div className="mt-2 flex items-center justify-between">
        <span className={`inline-flex items-center gap-1 text-[11px] font-medium ${accent.text}`}>
          <span className={`h-1.5 w-1.5 rounded-full ${accent.dot}`} />
          {job.status}
        </span>
        {job.url && (
          <a
            href={job.url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            onPointerDown={(e) => e.stopPropagation()}
            className="shrink-0 rounded p-1 text-slate-400 transition hover:bg-slate-100 hover:text-sky-600 dark:hover:bg-slate-700 dark:hover:text-sky-400"
            title="Open LinkedIn posting"
          >
            <LinkedInIcon />
          </a>
        )}
      </div>
    </div>
  )
}
