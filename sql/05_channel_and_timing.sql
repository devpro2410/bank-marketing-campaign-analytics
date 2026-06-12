-- ---------------------------------------------------------------------------
-- 05 | Channel engagement and timing
-- Cellular vs. landline performance month by month. Volume is included so the
-- rate isn't read in isolation: the high-converting autumn months are also the
-- low-volume months, which suggests the bank saturated its list in May.
-- ---------------------------------------------------------------------------
SELECT
    month_num,
    month,
    contact                                   AS channel,
    COUNT(*)                                  AS contacts,
    SUM(converted)                            AS conversions,
    ROUND(100.0 * AVG(converted), 1)          AS conversion_rate_pct
FROM contacts
GROUP BY month_num, month, contact
ORDER BY month_num, channel;
