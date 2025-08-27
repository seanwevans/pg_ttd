\set ON_ERROR_STOP on

BEGIN;

-- load schema and procedure definitions
\ir ../tables/companies.sql
\ir ../tables/vehicles.sql
\ir ../procs/move_vehicles.sql

-- allow NULL schedule_idx for testing
ALTER TABLE vehicles ALTER COLUMN schedule_idx DROP NOT NULL;

-- setup initial data
TRUNCATE vehicles RESTART IDENTITY;
INSERT INTO vehicles (x, y, schedule, schedule_idx)
VALUES (0, 0, '[{"x":0,"y":0},{"x":1,"y":0}]', NULL);

-- first move should reset schedule_idx and not move
CALL move_vehicles();
DO $$
BEGIN
    IF (SELECT schedule_idx FROM vehicles WHERE id = 1) != 1 THEN
        RAISE EXCEPTION 'schedule index not reset to 1';
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
        RAISE EXCEPTION 'vehicle did not move toward waypoint';
    END IF;
    IF (SELECT schedule_idx FROM vehicles WHERE id = 1) != 1 THEN
        RAISE EXCEPTION 'schedule index incorrect after movement';
    END IF;
END$$;

ROLLBACK;
