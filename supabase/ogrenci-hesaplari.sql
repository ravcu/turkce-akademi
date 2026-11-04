create table if not exists public.student_profiles (
 user_id uuid primary key references auth.users(id) on delete cascade,
 first_name text not null,
 last_name text not null,
 updated_at timestamptz default now()
);
create table if not exists public.student_progress (
 user_id uuid not null references auth.users(id) on delete cascade,
 progress_key text not null,
 payload jsonb not null,
 updated_at timestamptz default now(),
 primary key(user_id, progress_key)
);
alter table public.student_profiles enable row level security;
alter table public.student_progress enable row level security;
grant select,insert,update,delete on public.student_profiles to authenticated;
grant select,insert,update,delete on public.student_progress to authenticated;
create policy "profile select own" on public.student_profiles for select to authenticated using (auth.uid()=user_id);
create policy "profile insert own" on public.student_profiles for insert to authenticated with check (auth.uid()=user_id);
create policy "profile update own" on public.student_profiles for update to authenticated using (auth.uid()=user_id) with check (auth.uid()=user_id);
create policy "progress select own" on public.student_progress for select to authenticated using (auth.uid()=user_id);
create policy "progress insert own" on public.student_progress for insert to authenticated with check (auth.uid()=user_id);
create policy "progress update own" on public.student_progress for update to authenticated using (auth.uid()=user_id) with check (auth.uid()=user_id);