create table public.products (
  product_id uuid not null default gen_random_uuid (),
  category_id uuid null default gen_random_uuid (),
  name character varying not null,
  sku character varying not null,
  description text null,
  quantity_per_unit character varying null,
  unit_price numeric not null,
  discount numeric null default '0'::numeric,
  created_at timestamp with time zone not null default now(),
  constraint products_pkey primary key (product_id),
  constraint products_sku_key unique (sku),
  constraint products_category_id_fkey foreign KEY (category_id) references categories (category_id) on delete set null
) TABLESPACE pg_default;