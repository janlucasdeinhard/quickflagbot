-- Test: save test

SELECT 
    CASE 
        WHEN stage IN ('Proposal', 'Negotiation', 'Qualified', 'Won') THEN 'PASS'
        ELSE 'FAIL'
    END AS test_result
FROM 
    opportunities;
