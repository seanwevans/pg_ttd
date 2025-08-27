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
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    cash INTEGER NOT NULL DEFAULT 0,
    income INTEGER NOT NULL DEFAULT 0,
    expenses INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS industries (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    tile_id INTEGER NOT NULL REFERENCES tiles(id),
    company_id INTEGER REFERENCES companies(id)
);

CREATE TABLE IF NOT EXISTS vehicles (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    tile_id INTEGER NOT NULL REFERENCES tiles(id),
    company_id INTEGER NOT NULL REFERENCES companies(id)
);

CREATE TABLE IF NOT EXISTS industry_outputs (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    value INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS vehicle_operations (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    revenue INTEGER NOT NULL,
    cost INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS game_state (
    id SERIAL PRIMARY KEY,
    current_tick BIGINT DEFAULT 0,
    seed BIGINT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
