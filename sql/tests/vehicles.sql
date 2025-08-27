\set ON_ERROR_STOP on

BEGIN;

-- load table definitions
\ir ../tables/companies.sql
\ir ../tables/vehicles.sql

-- negative position should fail
DO $$
BEGIN
    BEGIN
        INSERT INTO vehicles (x, y) VALUES (-1, 0);
        RAISE EXCEPTION 'negative x allowed';
    EXCEPTION WHEN others THEN
        NULL;
    END;
    BEGIN
        INSERT INTO vehicles (x, y) VALUES (0, -1);
        RAISE EXCEPTION 'negative y allowed';
    EXCEPTION WHEN others THEN
        NULL;
    END;
END$$;

-- schedule_idx out of bounds on insert
DO $$
BEGIN
    BEGIN
        INSERT INTO vehicles (x, y, schedule, schedule_idx)
        VALUES (0, 0, '[{"x":1,"y":1}]', 2);
        RAISE EXCEPTION 'schedule_idx insert out of bounds allowed';
    EXCEPTION WHEN others THEN
        NULL;
    END;
    BEGIN
        INSERT INTO vehicles (x, y, schedule, schedule_idx)
        VALUES (0, 0, '[]', 1);
        RAISE EXCEPTION 'schedule_idx insert out of bounds for empty schedule allowed';
    EXCEPTION WHEN others THEN
        NULL;
    END;
END$$;

-- schedule_idx out of bounds on update
INSERT INTO vehicles (x, y, schedule, schedule_idx)
VALUES (0, 0, '[{"x":1,"y":1},{"x":2,"y":2}]', 0);

DO $$
BEGIN
    BEGIN
        UPDATE vehicles SET schedule_idx = 2 WHERE id = 1;
        RAISE EXCEPTION 'schedule_idx update out of bounds allowed';
    EXCEPTION WHEN others THEN
        NULL;
    END;
END$$;

ROLLBACK;
