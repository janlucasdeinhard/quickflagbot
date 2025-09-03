SELECT account_id,
       CASE
           WHEN opportunity_id IS NULL THEN 'FAIL'
           ELSE 'PASS'
       END as test_result
FROM transactions;