-- Resources available in the world economy
CREATE TABLE IF NOT EXISTS resources (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    amount INTEGER NOT NULL DEFAULT 0
);
