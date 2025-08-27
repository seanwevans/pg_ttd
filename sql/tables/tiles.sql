-- Grid tiles referencing terrain
CREATE TABLE IF NOT EXISTS tiles (
    id SERIAL PRIMARY KEY,
    x INTEGER NOT NULL,
    y INTEGER NOT NULL,
    terrain_id INTEGER NOT NULL REFERENCES terrain (id),
    UNIQUE (x, y)
);
