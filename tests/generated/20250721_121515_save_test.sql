-- Test: save test

SELECT CASE 
WHEN COUNT(*) = (SELECT MAX(id) FROM patients) THEN 1
ELSE 0
END
FROM patients;
