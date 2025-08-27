-- pg_ttd initial schema

CREATE TABLE IF NOT EXISTS terrain (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS tiles (
    id SERIAL PRIMARY KEY,
    x INTEGER NOT NULL,
    y INTEGER NOT NULL,
    terrain_id INTEGER NOT NULL REFERENCES terrain(id),
    UNIQUE (x, y)
);

CREATE TABLE IF NOT EXISTS companies (
    company_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    cash BIGINT NOT NULL DEFAULT 0,
    income BIGINT NOT NULL DEFAULT 0,
    expenses BIGINT NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS industries (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    tile_id INTEGER NOT NULL REFERENCES tiles(id),
    company_id INTEGER REFERENCES companies(company_id)
);

CREATE TABLE IF NOT EXISTS vehicles (
    id SERIAL PRIMARY KEY,
    x INTEGER NOT NULL,
    y INTEGER NOT NULL,
    schedule JSONB NOT NULL DEFAULT '[]'::jsonb,
    schedule_idx INTEGER NOT NULL DEFAULT 0,
    cargo JSONB NOT NULL DEFAULT '[]'::jsonb,
    company_id INTEGER REFERENCES companies(company_id)
);

CREATE TABLE IF NOT EXISTS game_state (
    id SERIAL PRIMARY KEY,
    current_tick BIGINT DEFAULT 0,
    seed BIGINT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
