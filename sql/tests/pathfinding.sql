\set ON_ERROR_STOP on

BEGIN;

-- load function under test
\ir ../procs/pathfinding.sql

-- verify simple route
DO $$
DECLARE
    res integer[][];
    expected integer[][] := ARRAY[[1,1],[2,1],[3,1],[3,2]];
BEGIN
    res := find_route(1,1,3,2);
    IF res IS NULL OR res != expected THEN
        RAISE EXCEPTION 'route mismatch: %', res;
    END IF;
END$$;

-- verify start equals end
DO $$
DECLARE
    res integer[][];
    expected integer[][] := ARRAY[[2,2]];
BEGIN
    res := find_route(2,2,2,2);
    IF res IS NULL OR res != expected THEN
        RAISE EXCEPTION 'single tile route mismatch: %', res;
    END IF;
END$$;

ROLLBACK;
