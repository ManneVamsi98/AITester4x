import { useEffect, useState } from 'react'
import { STATUSES } from '../constants.js'

const inputCls =
  'w-full rounded-md border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500'

const labelCls = 'mb-1 block text-xs font-medium text-slate-500 dark:text-slate-400'

export default function JobForm({ initial, resumeNames, onSubmit, onCancel, onDelete }) {
  const [form, setForm] = useState({
    company: '',
    role: '',
    url: '',
    resume: '',
    dateApplied: new Date().toISOString().slice(0, 10),
    followUpDate: '',
    salary: '',
    skills: '',
    notes: '',
    status: 'wishlist',
    ...initial,
  })
  const [errors, setErrors] = useState({})

  // Reset form whenever the modal switches between add/edit targets.
  useEffect(() => {
    setForm({
      company: '',
      role: '',
      url: '',
      resume: '',
      dateApplied: new Date().toISOString().slice(0, 10),
      followUpDate: '',
      salary: '',
      skills: '',
      notes: '',
      status: 'wishlist',
      ...initial,
    })
    setErrors({})
  }, [initial])

  const set = (field) => (e) => {
    setForm((f) => ({ ...f, [field]: e.target.value }))
    setErrors((er) => ({ ...er, [field]: undefined }))
  }

  function handleSubmit(e) {
    e.preventDefault()
    const errs = {}
    if (!form.company.trim()) errs.company = 'Company name is required'
    if (!form.role.trim()) errs.role = 'Job title / role is required'
    if (form.url && !/^https?:\/\/.+/i.test(form.url)) errs.url = 'Enter a valid URL (https://…)'
    if (!form.dateApplied) errs.dateApplied = 'Date applied is required'
    setErrors(errs)
    if (Object.keys(errs).length) return
    onSubmit({ ...form, company: form.company.trim(), role: form.role.trim(), url: form.url.trim(), resume: form.resume.trim(), salary: form.salary.trim(), notes: form.notes.trim() })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className={labelCls}>Company name *</label>
          <input className={inputCls} value={form.company} onChange={set('company')} placeholder="Acme Corp" autoFocus />
          {errors.company && <p className="mt-1 text-xs text-rose-500">{errors.company}</p>}
        </div>
        <div>
          <label className={labelCls}>Job title / role *</label>
          <input className={inputCls} value={form.role} onChange={set('role')} placeholder="Senior QA Engineer" />
          {errors.role && <p className="mt-1 text-xs text-rose-500">{errors.role}</p>}
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className={labelCls}>LinkedIn job URL</label>
          <input className={inputCls} value={form.url} onChange={set('url')} placeholder="https://www.linkedin.com/jobs/view/…" />
          {errors.url && <p className="mt-1 text-xs text-rose-500">{errors.url}</p>}
        </div>
        <div>
          <label className={labelCls}>Resume used</label>
          <input className={inputCls} value={form.resume} onChange={set('resume')} list="resume-names" placeholder="e.g. QA_Lead_Resume" />
          <datalist id="resume-names">
            {resumeNames.map((r) => (
              <option key={r} value={r} />
            ))}
          </datalist>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <div>
          <label className={labelCls}>Date applied</label>
          <input type="date" className={inputCls} value={form.dateApplied} onChange={set('dateApplied')} />
          {errors.dateApplied && <p className="mt-1 text-xs text-rose-500">{errors.dateApplied}</p>}
        </div>
        <div>
          <label className={labelCls}>Follow-up date (reminder)</label>
          <input type="date" className={inputCls} value={form.followUpDate} onChange={set('followUpDate')} />
        </div>
        <div>
          <label className={labelCls}>Salary range</label>
          <input className={inputCls} value={form.salary} onChange={set('salary')} placeholder="₹25-30 LPA" />
        </div>
        <div>
          <label className={labelCls}>Status</label>
          <select className={inputCls} value={form.status} onChange={set('status')}>
            {STATUSES.map((s) => (
              <option key={s.id} value={s.id}>
                {s.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className={labelCls}>Skills required</label>
          <input className={inputCls} value={form.skills} onChange={set('skills')} placeholder="e.g. Selenium, Java, API testing" />
        </div>
        <div>
          <label className={labelCls}>Notes</label>
          <textarea
            className={`${inputCls} resize-y`}
            rows={1}
            value={form.notes}
            onChange={set('notes')}
            placeholder="Recruiter name, referral info, interview tips…"
          />
        </div>
      </div>

      <div className="flex items-center justify-between gap-2 pt-1">
        {onDelete ? (
          <button type="button" onClick={onDelete} className="rounded-md border border-rose-300 px-4 py-2 text-sm font-medium text-rose-600 hover:bg-rose-50 dark:border-rose-800 dark:text-rose-400 dark:hover:bg-rose-950">
            Delete
          </button>
        ) : (
          <span />
        )}
        <div className="flex gap-2">
          <button type="button" onClick={onCancel} className="rounded-md border border-slate-300 dark:border-slate-600 px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700">
            Cancel
          </button>
          <button type="submit" className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">
            {initial ? 'Save changes' : 'Add job'}
          </button>
        </div>
      </div>
    </form>
  )
}
