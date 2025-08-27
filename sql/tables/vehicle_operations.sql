-- Temporary storage for vehicle revenue and costs per tick
CREATE TABLE IF NOT EXISTS vehicle_operations (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies (id),
    revenue INTEGER NOT NULL,
    cost INTEGER NOT NULL
);
