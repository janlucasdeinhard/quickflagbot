-- Test: save test

SELECT v.*
FROM visits v
LEFT JOIN patients p ON v.patient_id = p.id
WHERE p.id IS NULL;
