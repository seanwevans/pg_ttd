-- Table definition for terrain types
CREATE TABLE IF NOT EXISTS terrain (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
