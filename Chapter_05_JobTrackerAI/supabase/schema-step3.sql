-- ============================================================
-- STEP 3 of 3: Row-level security policies
-- Run ONLY this block AFTER steps 1 and 2 succeed.
-- ============================================================

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
