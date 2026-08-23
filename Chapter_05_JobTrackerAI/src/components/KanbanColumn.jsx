import { useDroppable } from '@dnd-kit/core'
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable'
import JobCard from './JobCard.jsx'
import { STATUS_ACCENT } from '../constants.js'

export default function KanbanColumn({ status, label, jobs, onEdit, onAdd, isOver }) {
  const { setNodeRef } = useDroppable({ id: status })
  const accent = STATUS_ACCENT[status] || STATUS_ACCENT.wishlist

  return (
    <div
      ref={setNodeRef}
      className={`flex max-h-full w-72 shrink-0 flex-col rounded-lg bg-slate-100 dark:bg-slate-900/60 ${
        isOver ? 'ring-2 ring-blue-500/70' : ''
      }`}
    >
      <div className={`flex items-center justify-between rounded-t-lg px-3 py-2.5 ${accent.header}`}>
        <div className="flex items-center gap-2">
          <span className={`h-2 w-2 rounded-full ${accent.dot}`} />
          <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-200">{label}</h2>
          <span className="rounded-full bg-white px-2 py-0.5 text-xs font-semibold text-slate-600 dark:bg-slate-800 dark:text-slate-300">
            {jobs.length}
          </span>
        </div>
        <button
          onClick={() => onAdd(status)}
          className="rounded p-1 text-slate-400 transition hover:bg-white/60 hover:text-slate-600 dark:hover:bg-slate-800 dark:hover:text-slate-200"
          title={`Add job to ${label}`}
        >
          <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2.5">
            <path d="M12 5v14M5 12h14" />
          </svg>
        </button>
      </div>

      <div className="flex-1 space-y-2 overflow-y-auto p-2">
        <SortableContext items={jobs.map((j) => j.id)} strategy={verticalListSortingStrategy}>
          {jobs.map((job) => (
            <JobCard key={job.id} job={job} onEdit={onEdit} />
          ))}
        </SortableContext>
        {jobs.length === 0 && (
          <div className="rounded-md border border-dashed border-slate-300 py-8 text-center text-xs text-slate-400 dark:border-slate-700">
            No jobs — drag here or add one
          </div>
        )}
      </div>
    </div>
  )
}
