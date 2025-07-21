-- Test: save test

SELECT 
    CASE 
        WHEN COUNT(*) = 0 THEN 1
        ELSE 0
    END
FROM 
    patients
WHERE 
    id IS NULL 
    OR name IS NULL 
    OR birth_date IS NULL;
