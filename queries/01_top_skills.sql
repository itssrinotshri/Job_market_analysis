-- Business Question 1:
-- Which skills/tools appear most frequently in Data Analyst postings overall?

WITH TotalPostings AS (
    SELECT COUNT(*) AS total_jobs FROM jobs
),
SkillCounts AS (
    SELECT 
        s.skill_name,
        s.category,
        COUNT(DISTINCT ps.job_id) AS posting_count
    FROM skills s
    JOIN posting_skills ps ON s.skill_name = ps.skill_name
    GROUP BY s.skill_name, s.category
)
SELECT 
    sc.skill_name,
    sc.category,
    sc.posting_count,
    ROUND(CAST(sc.posting_count AS REAL) * 100.0 / tp.total_jobs, 2) AS pct_of_total_jobs,
    DENSE_RANK() OVER (ORDER BY sc.posting_count DESC) AS skill_rank
FROM SkillCounts sc
CROSS JOIN TotalPostings tp
ORDER BY sc.posting_count DESC;
