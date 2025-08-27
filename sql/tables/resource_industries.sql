-- Industries that transform one resource into another
CREATE TABLE IF NOT EXISTS resource_industries (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    input_resource_id INTEGER REFERENCES resources (id),
    output_resource_id INTEGER REFERENCES resources (id),
    input_per_tick INTEGER NOT NULL DEFAULT 0,
    output_per_tick INTEGER NOT NULL DEFAULT 0
);
