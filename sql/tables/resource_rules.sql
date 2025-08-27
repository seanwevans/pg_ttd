-- Growth and decay rules for resources
CREATE TABLE IF NOT EXISTS resource_rules (
    resource_id INTEGER PRIMARY KEY REFERENCES resources (id) ON DELETE CASCADE,
    growth_rate INTEGER NOT NULL DEFAULT 0,
    decay_rate INTEGER NOT NULL DEFAULT 0
);
