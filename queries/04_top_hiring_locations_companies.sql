-- Business Question 4:
-- Which cities and companies have the highest posting volume for Data Analysts?

WITH TopCities AS (
    SELECT 
        'City' AS entity_type,
        city || ', ' || COALESCE(state, 'India') AS entity_name,
        COUNT(*) AS total_postings,
        ROUND(AVG(salary_imputed), 2) AS avg_salary_inr,
        DENSE_RANK() OVER (ORDER BY COUNT(*) DESC) AS ranking
    FROM jobs
    WHERE city IS NOT NULL AND city != 'Unspecified'
    GROUP BY city, state
),
TopCompanies AS (
    SELECT 
        'Company' AS entity_type,
        company AS entity_name,
        COUNT(*) AS total_postings,
        ROUND(AVG(salary_imputed), 2) AS avg_salary_inr,
        DENSE_RANK() OVER (ORDER BY COUNT(*) DESC) AS ranking
    FROM jobs
    WHERE company IS NOT NULL AND company != 'Unknown'
    GROUP BY company
)
SELECT entity_type, ranking, entity_name, total_postings, avg_salary_inr
FROM TopCities
WHERE ranking <= 10
UNION ALL
SELECT entity_type, ranking, entity_name, total_postings, avg_salary_inr
FROM TopCompanies
WHERE ranking <= 10
ORDER BY entity_type DESC, ranking ASC;
