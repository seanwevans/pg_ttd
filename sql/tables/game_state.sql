-- Singleton game state metadata
CREATE TABLE IF NOT EXISTS game_state (
    id SERIAL PRIMARY KEY,
    current_tick BIGINT DEFAULT 0,
    seed BIGINT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
