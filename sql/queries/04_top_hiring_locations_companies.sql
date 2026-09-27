-- Business Question 4:
-- Which cities and companies have the highest posting volume for Data Analysts?

-- Top Cities
SELECT 
    city,
    state,
    COUNT(*) AS total_postings,
    ROUND(AVG(salary_imputed), 2) AS avg_city_salary,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs), 2) AS pct_of_total_market
FROM jobs
WHERE city IS NOT NULL AND city != 'Unspecified'
GROUP BY city, state
ORDER BY total_postings DESC
LIMIT 15;
