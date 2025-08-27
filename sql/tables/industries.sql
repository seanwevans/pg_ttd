-- Industry structures placed on tiles
CREATE TABLE IF NOT EXISTS industries (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    tile_id INTEGER NOT NULL REFERENCES tiles (id),
    company_id INTEGER REFERENCES companies (id)
);
