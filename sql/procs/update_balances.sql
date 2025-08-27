-- Adjust company balances based on industry and vehicle activity
CREATE OR REPLACE FUNCTION update_balances()
RETURNS VOID AS $$
BEGIN
    -- Reset per-tick aggregates
    UPDATE companies SET income = 0, expenses = 0;

    -- Apply industry output as income
    UPDATE companies c
    SET
        income = income + COALESCE(io.total_output, 0),
        cash   = cash + COALESCE(io.total_output, 0)
    FROM (
        SELECT company_id, SUM(value) AS total_output
        FROM industry_outputs
        GROUP BY company_id
    ) io
    WHERE io.company_id = c.id;

    -- Apply vehicle operations
    UPDATE companies c
    SET
        income   = income + COALESCE(vo.revenue, 0),
        expenses = expenses + COALESCE(vo.cost, 0),
        cash     = cash + COALESCE(vo.revenue, 0) - COALESCE(vo.cost, 0)
    FROM (
        SELECT company_id,
               SUM(revenue) AS revenue,
               SUM(cost) AS cost
        FROM vehicle_operations
        GROUP BY company_id
    ) vo
    WHERE vo.company_id = c.id;
END;
$$ LANGUAGE plpgsql;
