-- Test: save test

SELECT t.account_id, t.opportunity_id,
       CASE
           WHEN a.account_id IS NULL THEN 'FAIL'
           ELSE 'PASS'
       END AS test_result
FROM transactions t
LEFT JOIN accounts a ON t.account_id = a.account_id;
