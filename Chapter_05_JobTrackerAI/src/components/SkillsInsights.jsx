import { useMemo, useState } from 'react'
import Modal from './Modal.jsx'

const STORAGE_KEY = 'job-tracker-skill-ratings'

function parseSkills(job) {
  if (!job.skills) return []
  return [...new Set(job.skills.split(',').map((s) => s.trim().toLowerCase()).filter(Boolean))]
}

function loadRatings() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {}
  } catch {
    return {}
  }
}

export default function SkillsInsights({ jobs, onClose }) {
  const [ratings, setRatings] = useState(loadRatings)

  const stats = useMemo(() => {
    const count = {}
    for (const job of jobs) {
      for (const skill of parseSkills(job)) {
        count[skill] = (count[skill] || 0) + 1
      }
    }
    const total = jobs.length || 1
    return Object.entries(count)
      .map(([skill, n]) => ({
        skill,
        count: n,
        pct: Math.round((n / total) * 100),
        rating: ratings[skill] || 3,
      }))
      .sort((a, b) => b.count - a.count || a.skill.localeCompare(b.skill))
  }, [jobs, ratings])

  const withRatings = stats.map((s) => ({ ...s, gap: s.count * (5 - s.rating) }))
  const roadmap = [...withRatings].sort((a, b) => b.gap - a.gap).slice(0, 8)

  function setRating(skill, value) {
    setRatings((prev) => {
      const next = { ...prev, [skill]: value }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
      return next
    })
  }

  const ratingLabel = (r) => ['', 'Novice', 'Beginner', 'Comfortable', 'Proficient', 'Expert'][r] || ''

  return (
    <Modal title="Skills insights" onClose={onClose}>
      {stats.length === 0 ? (
        <p className="text-sm text-slate-500 dark:text-slate-400">
          No skills recorded yet. Add comma-separated skills to a job (e.g. “Selenium, Java, API testing”) and they’ll show up here.
        </p>
      ) : (
        <div className="space-y-6">
          {/* Roadmap */}
          <div>
            <h3 className="mb-2 text-sm font-semibold text-slate-700 dark:text-slate-200">Your next learning roadmap</h3>
            <ol className="space-y-1.5">
              {roadmap.map((s, i) => (
                <li key={s.skill} className="flex items-center justify-between gap-2 rounded-md bg-slate-50 px-3 py-2 text-sm dark:bg-slate-800">
                  <span className="min-w-0 truncate">
                    <span className="mr-1.5 font-semibold text-slate-400">{i + 1}.</span>
                    <span className="font-medium capitalize">{s.skill}</span>
                  </span>
                  <span className="shrink-0 text-xs text-slate-500 dark:text-slate-400">
                    in {s.pct}% of jobs · rated {s.rating}/5
                  </span>
                </li>
              ))}
            </ol>
          </div>

          {/* Skill matrix */}
          <div>
            <h3 className="mb-2 text-sm font-semibold text-slate-700 dark:text-slate-200">Skill demand & gap</h3>
            <div className="overflow-hidden rounded-lg border border-slate-200 dark:border-slate-700">
              <table className="w-full text-sm">
                <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500 dark:bg-slate-800 dark:text-slate-400">
                  <tr>
                    <th className="px-3 py-2">Skill</th>
                    <th className="px-3 py-2">In jobs</th>
                    <th className="px-3 py-2">Your level</th>
                    <th className="px-3 py-2">Gap</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {withRatings.map((s) => (
                    <tr key={s.skill}>
                      <td className="px-3 py-2 font-medium capitalize">{s.skill}</td>
                      <td className="px-3 py-2 text-slate-500 dark:text-slate-400">
                        {s.count} ({s.pct}%)
                      </td>
                      <td className="px-3 py-2">
                        <select
                          value={s.rating}
                          onChange={(e) => setRating(s.skill, Number(e.target.value))}
                          title={ratingLabel(s.rating)}
                          className="rounded-md border border-slate-300 bg-white px-1.5 py-1 text-xs focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
                        >
                          {[1, 2, 3, 4, 5].map((r) => (
                            <option key={r} value={r}>{r} — {ratingLabel(r)}</option>
                          ))}
                        </select>
                      </td>
                      <td className="px-3 py-2">
                        <span className={`font-semibold ${s.gap >= 6 ? 'text-rose-600 dark:text-rose-400' : s.gap >= 3 ? 'text-amber-600 dark:text-amber-400' : 'text-emerald-600 dark:text-emerald-400'}`}>
                          {s.gap}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="mt-1 text-xs text-slate-400 dark:text-slate-500">
              Gap = how often the skill appears × (5 − your level). Higher gap = learn it first. Ratings are saved in this browser.
            </p>
          </div>
        </div>
      )}
    </Modal>
  )
}
