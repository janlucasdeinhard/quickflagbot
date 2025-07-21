-- Test: save test

SELECT CASE 
    WHEN EXISTS (
        SELECT 1 
        FROM patients p 
        JOIN visits v ON p.id = v.patient_id 
        WHERE v.visit_date < p.birth_date
    ) THEN 0 
    ELSE 1 
END;
