-- ---------------------------------------------------------------------------
-- 04 | Customer history: the strongest conversion signal
-- How does a client's relationship with previous campaigns shape the outcome
-- of this one? Combines previous-campaign outcome with recency of the last
-- contact (pdays is NULL for clients never contacted before).
-- ---------------------------------------------------------------------------
SELECT
    poutcome                                  AS previous_outcome,
    CASE
        WHEN pdays IS NULL    THEN 'never contacted'
        WHEN pdays <= 7       THEN 'within 1 week'
        WHEN pdays <= 30      THEN '1-4 weeks ago'
        ELSE                       'over a month ago'
    END                                       AS last_contact_recency,
    COUNT(*)                                  AS contacts,
    SUM(converted)                            AS conversions,
    ROUND(100.0 * AVG(converted), 1)          AS conversion_rate_pct
FROM contacts
GROUP BY 1, 2
ORDER BY conversion_rate_pct DESC;
