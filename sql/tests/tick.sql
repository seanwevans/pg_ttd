\set ON_ERROR_STOP on

BEGIN;

-- load procedure under test
\ir ../procs/tick.sql

-- setup game state and terrain
CREATE TABLE game_state (current_tick INT);
INSERT INTO game_state (current_tick) VALUES (0);
CREATE TABLE terrain (id SERIAL PRIMARY KEY, updated_tick INT);
INSERT INTO terrain DEFAULT VALUES;
INSERT INTO terrain DEFAULT VALUES;

-- execute tick
CALL tick();

-- verify tick counter and terrain updates
DO $$
BEGIN
    IF (SELECT current_tick FROM game_state) != 1 THEN
        RAISE EXCEPTION 'tick counter not incremented';
    END IF;
    IF EXISTS (SELECT 1 FROM terrain WHERE updated_tick <> 1) THEN
        RAISE EXCEPTION 'terrain not updated with tick';
    END IF;
END$$;

ROLLBACK;
