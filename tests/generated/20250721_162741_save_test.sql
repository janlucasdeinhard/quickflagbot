-- Test: save test

SELECT CASE 
    WHEN (
        SELECT COUNT(*) 
        FROM visits 
        WHERE patient_id NOT IN (SELECT id FROM patients)
    ) = 0 THEN 1 
    ELSE 0 
END;
