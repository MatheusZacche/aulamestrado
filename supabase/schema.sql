-- Schema do Aulamestrado para Supabase Postgres (versão single-user).
--
-- Como rodar:
--   1. Crie um projeto novo em https://supabase.com (free tier).
--   2. SQL Editor → cole este arquivo INTEIRO → Run.
--   3. Não precisa configurar Auth — esta versão é single-user, sem login.
--      A proteção dos dados é via a anon key que fica em Secrets do
--      Streamlit Cloud (privado, não vai pro repo).
--
-- Idempotente: pode rodar de novo sem destruir dados.

-- ============================================================
-- TABELAS
-- ============================================================

create table if not exists public.answers (
  question_id  text        primary key,
  chosen       text        not null check (chosen in ('a','b','c','d','e')),
  correct      boolean     not null,
  confianca    text        default '',
  ts           timestamptz not null default now()
);

create table if not exists public.bookmarks (
  question_id  text        primary key,
  ts           timestamptz not null default now()
);

create table if not exists public.notes (
  question_id  text        primary key,
  conteudo     text        not null default '',
  updated_at   timestamptz not null default now()
);

create table if not exists public.simulado_answers (
  question_id  text        primary key,
  chosen       text        not null check (chosen in ('a','b','c','d','e')),
  correct      boolean     not null,
  ts           timestamptz not null default now()
);

create table if not exists public.sessions (
  id           uuid             primary key default gen_random_uuid(),
  score        int              not null,
  total        int              not null,
  modo         text             not null,
  duration_s   double precision not null,
  ts           timestamptz      not null default now()
);

-- Índice útil para listar sessões mais recentes primeiro
create index if not exists idx_sessions_ts on public.sessions(ts desc);

-- ============================================================
-- ACESSO
-- Como o app é single-user e a anon key fica em Streamlit Secrets,
-- não precisamos de RLS — desabilitamos para que a anon key possa CRUD.
-- ============================================================

alter table public.answers           disable row level security;
alter table public.simulado_answers  disable row level security;
alter table public.bookmarks         disable row level security;
alter table public.notes             disable row level security;
alter table public.sessions          disable row level security;
