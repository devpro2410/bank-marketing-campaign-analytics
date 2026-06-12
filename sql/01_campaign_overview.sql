-- ---------------------------------------------------------------------------
-- 01 | Campaign overview KPIs
-- How big was the campaign, and what did it achieve overall?
-- ---------------------------------------------------------------------------
SELECT
    COUNT(*)                                          AS total_contacts,
    SUM(converted)                                    AS conversions,
    ROUND(100.0 * AVG(converted), 1)                  AS conversion_rate_pct,
    ROUND(AVG(campaign), 2)                           AS avg_contacts_per_client,
    ROUND(100.0 * AVG(CASE WHEN contact = 'cellular' THEN 1 ELSE 0 END), 1)
                                                      AS pct_via_cellular,
    ROUND(100.0 * AVG(previously_contacted), 1)       AS pct_with_prior_contact
FROM contacts;
