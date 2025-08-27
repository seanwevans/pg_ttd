-- Companies table with accounting fields
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    cash BIGINT NOT NULL DEFAULT 0,
    income BIGINT NOT NULL DEFAULT 0,
    expenses BIGINT NOT NULL DEFAULT 0
);
