-- Business Question 2:
-- How does the required skill set differ by seniority level (Entry / Mid / Senior / Lead)?

WITH SeniorityTotals AS (
    SELECT 
        seniority_level,
        COUNT(*) AS total_postings_in_tier
    FROM jobs
    GROUP BY seniority_level
),
SenioritySkillCounts AS (
    SELECT 
        j.seniority_level,
        s.skill_name,
        s.category,
        COUNT(DISTINCT j.job_id) AS skill_count
    FROM jobs j
    JOIN posting_skills ps ON j.job_id = ps.job_id
    JOIN skills s ON ps.skill_name = s.skill_name
    GROUP BY j.seniority_level, s.skill_name, s.category
),
RankedSkills AS (
    SELECT 
        ssc.seniority_level,
        ssc.skill_name,
        ssc.category,
        ssc.skill_count,
        st.total_postings_in_tier,
        ROUND(CAST(ssc.skill_count AS REAL) * 100.0 / st.total_postings_in_tier, 2) AS pct_in_tier,
        RANK() OVER (
            PARTITION BY ssc.seniority_level 
            ORDER BY ssc.skill_count DESC
        ) AS rank_within_tier
    FROM SenioritySkillCounts ssc
    JOIN SeniorityTotals st ON ssc.seniority_level = st.seniority_level
)
SELECT 
    seniority_level,
    rank_within_tier,
    skill_name,
    category,
    skill_count,
    total_postings_in_tier,
    pct_in_tier
FROM RankedSkills
WHERE rank_within_tier <= 10
ORDER BY seniority_level, rank_within_tier;
