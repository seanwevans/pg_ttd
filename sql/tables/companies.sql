-- Companies table for vehicle ownership and accounting
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    cash INTEGER NOT NULL DEFAULT 0,
    income INTEGER NOT NULL DEFAULT 0,
    expenses INTEGER NOT NULL DEFAULT 0
);
