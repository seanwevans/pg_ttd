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
    name TEXT NOT NULL UNIQUE
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

CREATE TABLE IF NOT EXISTS game_state (
    id SERIAL PRIMARY KEY,
    current_tick BIGINT DEFAULT 0,
    seed BIGINT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Resources available in the world economy
CREATE TABLE IF NOT EXISTS resources (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    amount INTEGER NOT NULL DEFAULT 0
);

-- Growth and decay rules for resources
CREATE TABLE IF NOT EXISTS resource_rules (
    resource_id INTEGER PRIMARY KEY REFERENCES resources(id) ON DELETE CASCADE,
    growth_rate INTEGER NOT NULL DEFAULT 0,
    decay_rate INTEGER NOT NULL DEFAULT 0
);

-- Industries that transform one resource into another
CREATE TABLE IF NOT EXISTS resource_industries (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    input_resource_id INTEGER REFERENCES resources(id),
    output_resource_id INTEGER REFERENCES resources(id),
    input_per_tick INTEGER NOT NULL DEFAULT 0,
    output_per_tick INTEGER NOT NULL DEFAULT 0
);
