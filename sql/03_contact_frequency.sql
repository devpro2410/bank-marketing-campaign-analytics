-- ---------------------------------------------------------------------------
-- 03 | Contact-frequency fatigue curve
-- Does calling the same client again improve the odds of conversion?
-- Reads per attempt number (capped at 10+) with cumulative effort vs. yield:
-- if 6+ contacts consume X% of all calls but deliver far less than X% of
-- conversions, that effort is better spent on fresh prospects.
-- ---------------------------------------------------------------------------
WITH per_attempt AS (
    SELECT
        LEAST(campaign, 10)                  AS n_contacts,   -- 10 = "10 or more"
        COUNT(*)                             AS clients,
        SUM(campaign)                        AS calls_made,
        SUM(converted)                       AS conversions
    FROM contacts
    GROUP BY 1
)
SELECT
    n_contacts,
    clients,
    conversions,
    ROUND(100.0 * conversions / clients, 1)                          AS conversion_rate_pct,
    ROUND(100.0 * calls_made / SUM(calls_made) OVER (), 1)           AS pct_of_all_calls,
    ROUND(100.0 * conversions / SUM(conversions) OVER (), 1)         AS pct_of_all_conversions
FROM per_attempt
ORDER BY n_contacts;
