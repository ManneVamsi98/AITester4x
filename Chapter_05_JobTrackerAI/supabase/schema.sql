-- Job Tracker AI — Supabase schema
-- Run this in the Supabase SQL editor. Re-running is safe (idempotent).

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

-- Migration for existing databases (already created before this column existed).
alter table public.jobs add column if not exists "followUpDate" text;
alter table public.jobs add column if not exists "skills" text;

-- Trigger to bump updated_at on change
create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists jobs_set_updated_at on public.jobs;
create trigger jobs_set_updated_at
  before update on public.jobs
  for each row execute function public.set_updated_at();

-- Row-level security: each user only sees their own rows
alter table public.jobs enable row level security;

drop policy if exists "Users select own jobs" on public.jobs;
create policy "Users select own jobs"
  on public.jobs for select
  using (auth.uid() = "user_id");

drop policy if exists "Users insert own jobs" on public.jobs;
create policy "Users insert own jobs"
  on public.jobs for insert
  with check (auth.uid() = "user_id");

drop policy if exists "Users update own jobs" on public.jobs;
create policy "Users update own jobs"
  on public.jobs for update
  using (auth.uid() = "user_id");

drop policy if exists "Users delete own jobs" on public.jobs;
create policy "Users delete own jobs"
  on public.jobs for delete
  using (auth.uid() = "user_id");
