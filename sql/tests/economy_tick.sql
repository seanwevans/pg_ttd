\set ON_ERROR_STOP on

BEGIN;

-- load schema and procedure definitions
\ir ../schema.sql
\ir ../procs/economy_tick.sql

-- setup initial data
TRUNCATE resources, resource_rules, resource_industries RESTART IDENTITY CASCADE;
INSERT INTO resources (name, amount) VALUES ('wood', 10), ('goods', 0);
INSERT INTO resource_rules (resource_id, growth_rate, decay_rate)
VALUES (1, 2, 0), (2, 0, 0);
INSERT INTO resource_industries (name, input_resource_id, output_resource_id, input_per_tick, output_per_tick)
VALUES ('sawmill', 1, 2, 3, 1);

-- execute tick
SELECT economy_tick();

-- verify results
DO $$
BEGIN
    IF (SELECT amount FROM resources WHERE name='wood') != 9 THEN
        RAISE EXCEPTION 'wood amount mismatch';
    END IF;
    IF (SELECT amount FROM resources WHERE name='goods') != 1 THEN
        RAISE EXCEPTION 'goods amount mismatch';
    END IF;
END$$;

ROLLBACK;
