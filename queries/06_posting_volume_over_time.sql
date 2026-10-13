-- Business Question 6:
-- What is the posting volume trend over time, comparing daily volumes with previous periods (LAG) and moving averages?

WITH DailyPostings AS (
    SELECT 
        SUBSTR(posted_date, 1, 10) AS posting_date,
        COUNT(*) AS daily_volume
    FROM jobs
    WHERE posted_date IS NOT NULL AND posted_date != ''
    GROUP BY SUBSTR(posted_date, 1, 10)
),
VolumeWithTrends AS (
    SELECT 
        posting_date,
        daily_volume,
        LAG(daily_volume, 1) OVER (ORDER BY posting_date) AS prev_day_volume,
        daily_volume - LAG(daily_volume, 1, daily_volume) OVER (ORDER BY posting_date) AS day_over_day_change,
        ROUND(AVG(daily_volume) OVER (
            ORDER BY posting_date 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ), 2) AS moving_avg_7d
    FROM DailyPostings
)
SELECT 
    posting_date,
    daily_volume,
    prev_day_volume,
    day_over_day_change,
    moving_avg_7d
FROM VolumeWithTrends
ORDER BY posting_date DESC
LIMIT 30;
