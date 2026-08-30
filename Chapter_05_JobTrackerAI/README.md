# My Job Tracker AI Buddy

A cloud-synced Kanban job tracker built with React + Vite + Tailwind CSS.
Data is stored in **Supabase** (Postgres), so your board is the same in every browser and protected behind **email/password login**. Live demo: **https://myjobtrackeraibuddy.vercel.app**

## Getting started

```bash
npm install
```

### 1. Create a Supabase project
1. Go to https://supabase.com and create a project (free tier is fine).
2. Open **SQL Editor** and run the schema **one file at a time** (running the full script at once can hit a transient "Backend error"):
   - `supabase/schema-step1.sql` — creates the `jobs` table
   - `supabase/schema-step2.sql` — adds the `updated_at` trigger
   - `supabase/schema-step3.sql` — enables row-level security + policies

   (`supabase/schema.sql` is the combined version; the step files are the reliable path.)

### 2. Configure environment
Create a `.env` file in this directory (copy from `.env.example`):

```bash
VITE_SUPABASE_URL=https://your-project-ref.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

Find both values in the Supabase dashboard under **Project Settings → API**. The anon key is safe to expose in the frontend — row-level security protects the data. If you deploy via the Vercel CLI, add `Vercel=<token>` (an account token from vercel.com/account/tokens) to the same `.env`.

### 3. Run

```bash
npm run dev
```

Open the printed local URL (default http://localhost:5173), sign up with an email + password, and you're in. Any jobs that previously lived in this browser's local storage are uploaded automatically on first sign-in.

## Features

- **Kanban board** with 6 columns: Wishlist → Applied → Follow-up → Interview → Offer → Rejected
- **Drag-and-drop** cards between columns (and reorder within a column) via `@dnd-kit`
- **Add / edit / delete** jobs — edit inline via a modal, delete with confirmation
- Card shows company, role, resume tag, days since applied, salary, and a clickable LinkedIn link
- **Follow-up reminders** — set an optional follow-up date per job; the card shows a bell badge ("Follow up in 2d", "Due today", "Overdue by 3d") and highlights overdue cards
- **Skills insights** — tag each job with the skills it asks for; a Skills panel ranks in-demand skills, lets you rate your own level, and suggests a learning roadmap based on your gaps
- **Login required** — each account only sees its own jobs
- **Cloud sync** — the same data appears in every browser/device
- **Sync-failure alerts** — if a save only lands locally, an amber banner warns you instead of failing silently
- **Search / filter** by company or role, plus **filter by date** (year, month, day)
- **Light / dark mode** toggle (follows system preference by default)
- **Export** all data as JSON, **import** JSON to restore (optional manual backup)
- Required-field validation on the form
- Responsive layout for laptop and tablet

## Deploying to Vercel

1. Push this repo to GitHub.
2. Import the repo in Vercel (framework preset: **Vite**; build `npm run build`, output `dist`), or deploy via the CLI:
   ```bash
   vercel --prod --yes --token <token> --name myjobtrackeraibuddy \
     -e VITE_SUPABASE_URL=... -e VITE_SUPABASE_ANON_KEY=...
   ```
3. Add the two environment variables (`VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`) in Vercel project settings so future builds have them automatically.
4. Deploy — sign in with the same account and your jobs are already there.

> **Note:** the free Supabase tier can auto-pause a project after ~1 week of inactivity. If the SQL editor later shows a "Backend error" or the app loses cloud sync, check for the "Project paused" banner in the dashboard and click **Restore**.

## Tech stack

- React 18 + Vite
- Tailwind CSS 3
- Supabase (`@supabase/supabase-js`) for auth + Postgres storage
- `idb` for a local IndexedDB mirror (offline fallback)
- `@dnd-kit/core` + `@dnd-kit/sortable` for drag-and-drop

## Data model

Each job stores: `company`, `role`, `url`, `resume`, `dateApplied`, `salary`, `notes`, `status`, plus optional `followUpDate` (reminder) and `skills`. Rows are owned by `user_id` (Supabase auth) and protected by row-level security.

## Backup / restore

Cloud storage makes backups automatic. The **Export** button still downloads `job-tracker-backup-YYYY-MM-DD.json` as an extra safety net, and **Import** loads it back (merges/overwrites by job `id`).
