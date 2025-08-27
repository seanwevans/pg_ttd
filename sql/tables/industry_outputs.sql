-- Temporary storage for industry production results per tick
CREATE TABLE IF NOT EXISTS industry_outputs (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL,
    value INTEGER NOT NULL
);

