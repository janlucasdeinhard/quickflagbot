-- Test: save test

SELECT CASE 
    WHEN (
        SELECT SUM(1) 
        FROM visits 
        WHERE patient_id NOT IN (SELECT id FROM patients)
    ) IS NULL THEN 1 
    ELSE 0 
END;
