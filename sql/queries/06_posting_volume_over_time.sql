-- Business Question 6:
-- How are job postings distributed by search term and date?

SELECT 
    search_term,
    remote_status,
    COUNT(*) AS total_postings,
    ROUND(AVG(salary_imputed), 2) AS avg_salary,
    MIN(posted_date) AS earliest_posting,
    MAX(posted_date) AS latest_posting
FROM jobs
GROUP BY search_term, remote_status
ORDER BY total_postings DESC;
