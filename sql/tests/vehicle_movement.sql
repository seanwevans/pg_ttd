\set ON_ERROR_STOP on

BEGIN;

-- load schema and function under test
\ir ../tables/vehicles.sql
\ir ../procs/pathfinding.sql
\ir ../procs/vehicle_movement.sql

-- setup a vehicle starting at (1,1)
TRUNCATE vehicles RESTART IDENTITY;
INSERT INTO vehicles (x, y) VALUES (1, 1);

-- move along route (1,1) -> (3,2)
SELECT move_vehicle(1, 1, 1, 3, 2);
DO $$
DECLARE vx int; vy int; idx int; BEGIN
    SELECT x, y, next_waypoint_idx INTO vx, vy, idx FROM vehicles WHERE id = 1;
    IF vx != 2 OR vy != 1 OR idx != 3 THEN
        RAISE EXCEPTION 'step1 mismatch: %, %, %', vx, vy, idx;
    END IF;
END$$;

SELECT move_vehicle(1, 1, 1, 3, 2);
DO $$
DECLARE vx int; vy int; idx int; BEGIN
    SELECT x, y, next_waypoint_idx INTO vx, vy, idx FROM vehicles WHERE id = 1;
    IF vx != 3 OR vy != 1 OR idx != 4 THEN
        RAISE EXCEPTION 'step2 mismatch: %, %, %', vx, vy, idx;
    END IF;
END$$;

SELECT move_vehicle(1, 1, 1, 3, 2);
DO $$
DECLARE vx int; vy int; idx int; BEGIN
    SELECT x, y, next_waypoint_idx INTO vx, vy, idx FROM vehicles WHERE id = 1;
    IF vx != 3 OR vy != 2 OR idx != 5 THEN
        RAISE EXCEPTION 'step3 mismatch: %, %, %', vx, vy, idx;
    END IF;
END$$;

ROLLBACK;

