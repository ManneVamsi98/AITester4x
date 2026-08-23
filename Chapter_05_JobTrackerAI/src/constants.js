export const STATUSES = [
  { id: 'wishlist', label: 'Wishlist' },
  { id: 'applied', label: 'Applied' },
  { id: 'followup', label: 'Follow-up' },
  { id: 'interview', label: 'Interview' },
  { id: 'offer', label: 'Offer' },
  { id: 'rejected', label: 'Rejected' },
]

export const STATUS_ORDER = STATUSES.map((s) => s.id)

export const STATUS_LABEL = Object.fromEntries(STATUSES.map((s) => [s.id, s.label]))

// Tailwind classes for the left-border accent and column accent per status.
export const STATUS_ACCENT = {
  wishlist: { border: 'border-l-sky-500', dot: 'bg-sky-500', text: 'text-sky-600 dark:text-sky-400', header: 'bg-sky-500/10' },
  applied: { border: 'border-l-blue-500', dot: 'bg-blue-500', text: 'text-blue-600 dark:text-blue-400', header: 'bg-blue-500/10' },
  followup: { border: 'border-l-violet-500', dot: 'bg-violet-500', text: 'text-violet-600 dark:text-violet-400', header: 'bg-violet-500/10' },
  interview: { border: 'border-l-amber-500', dot: 'bg-amber-500', text: 'text-amber-600 dark:text-amber-400', header: 'bg-amber-500/10' },
  offer: { border: 'border-l-emerald-500', dot: 'bg-emerald-500', text: 'text-emerald-600 dark:text-emerald-400', header: 'bg-emerald-500/10' },
  rejected: { border: 'border-l-rose-500', dot: 'bg-rose-500', text: 'text-rose-600 dark:text-rose-400', header: 'bg-rose-500/10' },
}
