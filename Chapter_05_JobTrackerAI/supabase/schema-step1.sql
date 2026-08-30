-- ============================================================
-- STEP 1 of 3: Create the jobs table
-- Run ONLY this block in the SQL editor, then check success.
-- ============================================================

create table if not exists public.jobs (
  "id" text primary key,
  "user_id" uuid not null default auth.uid() references auth.users (id) on delete cascade,
  "company" text not null,
  "role" text not null,
  "url" text,
  "resume" text,
  "dateApplied" text,
  "salary" text,
  "notes" text,
  "status" text not null default 'wishlist',
  "followUpDate" text,
  "skills" text,
  "created_at" timestamptz not null default now(),
  "updated_at" timestamptz not null default now()
);

-- Migration for existing databases (safe to include).
alter table public.jobs add column if not exists "followUpDate" text;
alter table public.jobs add column if not exists "skills" text;
