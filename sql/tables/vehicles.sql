-- Table definition for vehicles
CREATE TABLE IF NOT EXISTS vehicles (
    id SERIAL PRIMARY KEY,
    x INTEGER NOT NULL,
    y INTEGER NOT NULL,
    schedule JSONB NOT NULL DEFAULT '[]'::JSONB,
    schedule_idx INTEGER NOT NULL DEFAULT 0,
    cargo JSONB NOT NULL DEFAULT '[]'::JSONB,
    company_id INTEGER
);
