-- AI Contest Radar schema
-- Run once in Supabase SQL Editor.

create extension if not exists pgcrypto;

create table if not exists public.contests (
  id uuid primary key default gen_random_uuid(),
  fingerprint text not null unique,
  title text not null,
  organizer text,
  deadline date,
  prize_text text,
  total_prize_won bigint,
  eligibility text,
  categories text[] not null default '{}',
  ai_requirement text not null default 'unknown'
    check (ai_requirement in ('required', 'allowed', 'restricted', 'prohibited', 'unknown')),
  ai_reason text,
  ai_confidence numeric(4,3)
    check (ai_confidence is null or (ai_confidence >= 0 and ai_confidence <= 1)),
  summary text,
  source text not null,
  source_url text not null,
  first_seen_at timestamptz not null default now(),
  last_checked_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists contests_deadline_idx
  on public.contests (deadline asc nulls last);

create index if not exists contests_created_at_idx
  on public.contests (created_at desc);

create index if not exists contests_ai_requirement_idx
  on public.contests (ai_requirement);

create index if not exists contests_categories_gin_idx
  on public.contests using gin (categories);

alter table public.contests enable row level security;

drop policy if exists "Public can read contests" on public.contests;
create policy "Public can read contests"
on public.contests
for select
to anon, authenticated
using (true);

-- No public INSERT/UPDATE/DELETE policies.
-- The crawler writes using the service_role/secret key only.

create or replace function public.set_updated_at()
returns trigger
language plpgsql
security invoker
set search_path = ''
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists contests_set_updated_at on public.contests;
create trigger contests_set_updated_at
before update on public.contests
for each row execute function public.set_updated_at();
