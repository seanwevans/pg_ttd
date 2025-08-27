-- Retrieve the balance sheet for a single company
SELECT
    company_id,
    name,
    cash,
    income,
    expenses
FROM companies
WHERE company_id = :company_id;
