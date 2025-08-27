# Finance

Companies maintain basic accounting fields to track their financial state:

- `cash` – total available money.
- `income` – earnings generated in the current tick.
- `expenses` – money spent in the current tick.

Industry production and vehicle activity are recorded in the `industry_outputs`
and `vehicle_operations` tables respectively. Each row in these tables captures
the results for a single company during the current tick.

The `update_balances()` procedure runs every tick to apply results of industry
production and vehicle operations:

1. `income` and `expenses` are reset to zero.
2. Industry output increases both `income` and `cash`.
3. Vehicle revenue increases `income` and `cash` while operating costs increase
   `expenses` and reduce `cash`.

Use `reports/balance_sheet.sql` to inspect a company’s current financial
position.
