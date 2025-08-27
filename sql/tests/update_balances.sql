\set ON_ERROR_STOP on

BEGIN;

-- load table definitions and function under test
\ir ../tables/companies.sql
\ir ../tables/industry_outputs.sql
\ir ../tables/vehicle_operations.sql
\ir ../procs/update_balances.sql

-- setup initial data
INSERT INTO companies (name, cash, income, expenses)
VALUES ('Acme', 100, 10, 20);
INSERT INTO industry_outputs (company_id, value) VALUES (1, 50);
INSERT INTO vehicle_operations (company_id, revenue, cost)
VALUES (1, 30, 10);

-- execute function
SELECT update_balances();

-- verify results
DO $$
BEGIN
    IF (SELECT cash FROM companies WHERE id = 1) <> 170 THEN
        RAISE EXCEPTION 'cash mismatch';
    END IF;
    IF (SELECT income FROM companies WHERE id = 1) <> 80 THEN
        RAISE EXCEPTION 'income mismatch';
    END IF;
    IF (SELECT expenses FROM companies WHERE id = 1) <> 10 THEN
        RAISE EXCEPTION 'expenses mismatch';
    END IF;
END$$;

ROLLBACK;
