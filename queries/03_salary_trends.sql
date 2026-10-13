-- Business Question 3:
-- What are the compensation benchmarks across Remote vs Onsite roles, Seniority Tiers, and Hiring Locations?

SELECT 
    remote_status,
    COALESCE(city, 'Unspecified') AS city,
    seniority_level,
    COUNT(*) AS posting_count,
    ROUND(AVG(salary_imputed), 2) AS avg_salary_inr,
    ROUND(MIN(salary_imputed), 2) AS min_salary_inr,
    ROUND(MAX(salary_imputed), 2) AS max_salary_inr
FROM jobs
WHERE city IS NOT NULL AND city != 'Unspecified'
GROUP BY remote_status, city, seniority_level
HAVING COUNT(*) >= 3
ORDER BY posting_count DESC, avg_salary_inr DESC;
