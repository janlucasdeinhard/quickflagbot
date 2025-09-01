-- Test: save test

SELECT o.opportunity_id,
       CASE
           WHEN a.account_id IS NULL THEN 'FAIL'
           ELSE 'PASS'
       END AS test_result
FROM opportunities o
LEFT JOIN accounts a ON o.account_id = a.account_id;
