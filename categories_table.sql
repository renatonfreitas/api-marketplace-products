create table public.categories (
  category_id uuid not null default gen_random_uuid (),
  name character varying not null,
  created_at timestamp with time zone not null default now(),
  constraint categories_pkey primary key (category_id)
) TABLESPACE pg_default;