-- ---------------------------------------------------------------------------
-- 02 | Conversion by customer segment
-- Which demographic segments respond best to the term-deposit offer?
-- GROUPING SETS produces every segment cut in a single pass; the `dimension`
-- column tells the consumer (charts / Tableau) which cut a row belongs to.
-- ---------------------------------------------------------------------------
WITH segmented AS (
    SELECT
        CASE
            WHEN GROUPING(job) = 0             THEN 'job'
            WHEN GROUPING(age_band) = 0        THEN 'age_band'
            WHEN GROUPING(education_group) = 0 THEN 'education'
            WHEN GROUPING(marital) = 0         THEN 'marital'
        END                                       AS dimension,
        COALESCE(job, age_band::VARCHAR, education_group, marital) AS segment,
        COUNT(*)                                  AS contacts,
        SUM(converted)                            AS conversions,
        ROUND(100.0 * AVG(converted), 1)          AS conversion_rate_pct
    FROM contacts
    GROUP BY GROUPING SETS ((job), (age_band), (education_group), (marital))
)
SELECT *
FROM segmented
ORDER BY dimension, conversion_rate_pct DESC;
