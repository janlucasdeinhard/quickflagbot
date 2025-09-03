SELECT 
    CASE
        WHEN account_name IS NULL THEN 'FAIL'
        ELSE 'PASS'
    END as test_result
FROM 
    accounts;