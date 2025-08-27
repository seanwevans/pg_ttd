\set ON_ERROR_STOP on

BEGIN;

-- load schema and procedure definitions
\ir ../tables/vehicles.sql
\ir ../procs/move_vehicles.sql

-- setup initial data
TRUNCATE vehicles RESTART IDENTITY;
INSERT INTO vehicles (x, y, schedule)
VALUES (0, 0, '[{"x":0,"y":0},{"x":1,"y":0}]');

-- first move should advance schedule without moving
CALL move_vehicles();
DO $$
BEGIN
    IF (SELECT schedule_idx FROM vehicles WHERE id = 1) != 1 THEN
        RAISE EXCEPTION 'schedule did not advance';
    END IF;
    IF (SELECT x FROM vehicles WHERE id = 1) != 0 OR
       (SELECT y FROM vehicles WHERE id = 1) != 0 THEN
        RAISE EXCEPTION 'vehicle moved unexpectedly';
    END IF;
END$$;

-- second move should move toward next waypoint
CALL move_vehicles();
DO $$
BEGIN
    IF (SELECT x FROM vehicles WHERE id = 1) != 1 OR
       (SELECT y FROM vehicles WHERE id = 1) != 0 THEN
        RAISE EXCEPTION 'vehicle did not reach expected coordinates';
    END IF;
    IF (SELECT schedule_idx FROM vehicles WHERE id = 1) != 1 THEN
        RAISE EXCEPTION 'schedule index incorrect after movement';
    END IF;
END$$;

ROLLBACK;
