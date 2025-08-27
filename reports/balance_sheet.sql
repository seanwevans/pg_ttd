-- Retrieve the balance sheet for a single company
SELECT
    id,
    name,
    cash,
    income,
    expenses
FROM companies
WHERE id = :id;
