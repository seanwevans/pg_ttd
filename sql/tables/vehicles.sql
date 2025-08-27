-- Table definition for vehicles
CREATE TABLE IF NOT EXISTS vehicles (
    id SERIAL PRIMARY KEY,
    x INTEGER NOT NULL,
    y INTEGER NOT NULL,
    CONSTRAINT non_negative_position CHECK (x >= 0 AND y >= 0),
    schedule JSONB NOT NULL DEFAULT '[]'::JSONB,
    schedule_idx INTEGER NOT NULL DEFAULT 0,
    next_waypoint_idx INTEGER NOT NULL DEFAULT 1,
    CONSTRAINT schedule_idx_within_bounds
    CHECK (
        schedule_idx >= 0
        AND schedule_idx < GREATEST(JSONB_ARRAY_LENGTH(schedule), 1)
    ),
    cargo JSONB NOT NULL DEFAULT '[]'::JSONB,
    company_id INTEGER
);
