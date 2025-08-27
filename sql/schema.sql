-- Auto-generated; do not edit directly.

-- Table definition for terrain types
CREATE TABLE IF NOT EXISTS terrain (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

-- Grid tiles referencing terrain
CREATE TABLE IF NOT EXISTS tiles (
    id SERIAL PRIMARY KEY,
    x INTEGER NOT NULL,
    y INTEGER NOT NULL,
    terrain_id INTEGER NOT NULL REFERENCES terrain (id),
    UNIQUE (x, y)
);

-- Companies table for vehicle ownership and accounting
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    cash INTEGER NOT NULL DEFAULT 0,
    income INTEGER NOT NULL DEFAULT 0,
    expenses INTEGER NOT NULL DEFAULT 0
);

-- Industry structures placed on tiles
CREATE TABLE IF NOT EXISTS industries (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    tile_id INTEGER NOT NULL REFERENCES tiles (id),
    company_id INTEGER REFERENCES companies (id)
);

-- Table definition for vehicles
CREATE TABLE IF NOT EXISTS vehicles (
    id SERIAL PRIMARY KEY,
    x INTEGER NOT NULL,
    y INTEGER NOT NULL,
    schedule JSONB NOT NULL DEFAULT '[]'::JSONB,
    schedule_idx INTEGER NOT NULL DEFAULT 0,
    cargo JSONB NOT NULL DEFAULT '[]'::JSONB,
    company_id INTEGER REFERENCES companies (id)
);

-- Temporary storage for industry production results per tick
CREATE TABLE IF NOT EXISTS industry_outputs (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies (id),
    value INTEGER NOT NULL
);

-- Temporary storage for vehicle revenue and costs per tick
CREATE TABLE IF NOT EXISTS vehicle_operations (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies (id),
    revenue INTEGER NOT NULL,
    cost INTEGER NOT NULL
);

-- Singleton game state metadata
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
    resource_id INTEGER PRIMARY KEY REFERENCES resources (id) ON DELETE CASCADE,
    growth_rate INTEGER NOT NULL DEFAULT 0,
    decay_rate INTEGER NOT NULL DEFAULT 0
);

-- Industries that transform one resource into another
CREATE TABLE IF NOT EXISTS resource_industries (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    input_resource_id INTEGER REFERENCES resources (id),
    output_resource_id INTEGER REFERENCES resources (id),
    input_per_tick INTEGER NOT NULL DEFAULT 0,
    output_per_tick INTEGER NOT NULL DEFAULT 0
);

