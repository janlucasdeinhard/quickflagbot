-- Test: save test

SELECT 
    CASE 
        WHEN COUNT(*) = 0 THEN 1
        ELSE 0
    END
FROM 
    visits
WHERE 
    patient_id NOT IN (SELECT id FROM patients);
