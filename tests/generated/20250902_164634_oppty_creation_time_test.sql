SELECT 
    CASE
        WHEN strftime('%Y-%m-%d %H:%M:%S', created_at) IS NULL THEN 'FAIL'
        ELSE 'PASS'
    END AS 'test_result'
FROM opportunities;