-- Business Question 3:
-- What are the compensation benchmarks across Remote vs Onsite roles and Seniority Tiers?

SELECT 
    seniority_level,
    remote_status,
    COUNT(*) AS posting_count,
    ROUND(AVG(salary_imputed), 2) AS avg_salary_inr,
    ROUND(MIN(salary_imputed), 2) AS min_salary_inr,
    ROUND(MAX(salary_imputed), 2) AS max_salary_inr
FROM jobs
GROUP BY seniority_level, remote_status
ORDER BY avg_salary_inr DESC;
