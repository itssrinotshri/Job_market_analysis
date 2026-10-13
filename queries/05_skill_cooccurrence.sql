-- Business Question 5:
-- Which skills tend to co-occur in the same job posting (e.g., SQL + Tableau vs SQL + Python)?

WITH TotalJobs AS (
    SELECT COUNT(*) AS total_postings FROM jobs
),
SkillPairs AS (
    SELECT 
        ps1.skill_name AS skill_a,
        ps2.skill_name AS skill_b,
        COUNT(DISTINCT ps1.job_id) AS pair_frequency
    FROM posting_skills ps1
    JOIN posting_skills ps2 
        ON ps1.job_id = ps2.job_id 
       AND ps1.skill_name < ps2.skill_name
    GROUP BY ps1.skill_name, ps2.skill_name
)
SELECT 
    sp.skill_a,
    sp.skill_b,
    sp.pair_frequency,
    ROUND(CAST(sp.pair_frequency AS REAL) * 100.0 / tj.total_postings, 2) AS pct_of_all_jobs,
    DENSE_RANK() OVER (ORDER BY sp.pair_frequency DESC) AS pair_rank
FROM SkillPairs sp
CROSS JOIN TotalJobs tj
ORDER BY sp.pair_frequency DESC
LIMIT 25;
