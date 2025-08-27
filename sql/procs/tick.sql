CREATE OR REPLACE PROCEDURE tick()
LANGUAGE plpgsql
AS $$
DECLARE
    new_tick INT;
BEGIN
    -- Advance global tick counter
    UPDATE game_state
    SET current_tick = current_tick + 1
    RETURNING current_tick INTO new_tick;

    -- Example time-dependent update: mark terrain with latest tick
    UPDATE terrain SET updated_tick = new_tick;
END;
$$;
