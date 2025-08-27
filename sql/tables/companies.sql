-- Minimal companies table for vehicle ownership
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    cash INTEGER NOT NULL DEFAULT 0,
    income INTEGER NOT NULL DEFAULT 0,
    expenses INTEGER NOT NULL DEFAULT 0
);
