\set ON_ERROR_STOP on

BEGIN;

-- Minimal terrain setup for pathfinding tests
CREATE TEMP TABLE terrain(
    tile_x int,
    tile_y int,
    type text
);
INSERT INTO terrain(tile_x, tile_y, type)
SELECT x, y, 'plain'
FROM generate_series(1,3) x CROSS JOIN generate_series(1,3) y;
-- Mark a water tile to ensure impassable terrain is skipped
UPDATE terrain SET type = 'water' WHERE tile_x = 2 AND tile_y = 1;

-- load function under test
\ir ../procs/pathfinding.sql

-- verify simple route around impassable water tile
DO $$
DECLARE
    res integer[][];
    expected integer[][] := ARRAY[ARRAY[1,1], ARRAY[1,2], ARRAY[2,2], ARRAY[3,2]];
BEGIN
    res := find_route(1,1,3,2);
    IF res IS NULL OR res != expected THEN
        RAISE EXCEPTION 'route mismatch: %', res;
    END IF;
END$$;

-- verify optional cost map parameter is accepted
DO $$
DECLARE
    res integer[][];
    expected integer[][] := ARRAY[ARRAY[1,1], ARRAY[1,2], ARRAY[2,2], ARRAY[3,2]];
BEGIN
    res := find_route(1,1,3,2, ARRAY[ARRAY[1,2,5]]);
    IF res IS NULL OR res != expected THEN
        RAISE EXCEPTION 'weighted route mismatch: %', res;
    END IF;
END$$;

-- verify start equals end
DO $$
DECLARE
    res integer[][];
    expected integer[][] := ARRAY[ARRAY[2,2]];
BEGIN
    res := find_route(2,2,2,2);
    IF res IS NULL OR res != expected THEN
        RAISE EXCEPTION 'single tile route mismatch: %', res;
    END IF;
END$$;

ROLLBACK;

