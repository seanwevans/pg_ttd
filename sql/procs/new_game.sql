CREATE OR REPLACE PROCEDURE new_game(width INT, height INT)
LANGUAGE plpgsql
AS $$
DECLARE
    x INT;
    y INT;
BEGIN
    -- Reset world state
    TRUNCATE TABLE tiles RESTART IDENTITY CASCADE;
    TRUNCATE TABLE terrain RESTART IDENTITY CASCADE;
    TRUNCATE TABLE game_state RESTART IDENTITY CASCADE;

    -- Create initial game state
    INSERT INTO game_state(width, height, current_tick)
    VALUES (width, height, 0);

    -- Populate tiles and terrain
    FOR x IN 1..width LOOP
        FOR y IN 1..height LOOP
            INSERT INTO tiles(x, y) VALUES (x, y);
            INSERT INTO terrain(tile_x, tile_y, type)
            VALUES (x, y, 'plain');
        END LOOP;
    END LOOP;
END;
$$;
