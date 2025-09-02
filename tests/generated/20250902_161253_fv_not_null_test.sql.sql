SELECT CASE
    WHEN funnel_value IS NULL THEN 'FAIL'
    ELSE 'PASS'
END AS test_result
FROM opportunities;