# Job Tracker AI

A local-first Kanban job tracker built with React + Vite + Tailwind CSS.
All data is stored in the browser using IndexedDB (via the `idb` wrapper).
No backend, no auth, no API calls — 100% local.

## Getting started

```bash
npm install
npm run dev
```

Open the printed local URL (default http://localhost:5173).

## Features

- **Kanban board** with 6 columns: Wishlist → Applied → Follow-up → Interview → Offer → Rejected
- **Drag-and-drop** cards between columns (and reorder within a column) via `@dnd-kit`
- **Add / edit / delete** jobs — edit inline via a modal, delete with confirmation
- Card shows company, role, resume tag, days since applied, salary, and a clickable LinkedIn link
- Column headers show live card counts
- **Search / filter** by company name or role
- **Light / dark mode** toggle (follows system preference by default)
- **Export** all data as JSON, **import** JSON to restore
- Required-field validation on the form
- Responsive layout for laptop and tablet

## Tech stack

- React 18 + Vite
- Tailwind CSS 3
- `idb` for IndexedDB
- `@dnd-kit/core` + `@dnd-kit/sortable` for drag-and-drop

## Data model

Each job stores: `company`, `role`, `url`, `resume`, `dateApplied`, `salary`, `notes`, `status`.

## Backup / restore

Use the **Export** button in the header to download `job-tracker-backup-YYYY-MM-DD.json`.
Use **Import** to load it back (merges/overwrites by job `id`).
