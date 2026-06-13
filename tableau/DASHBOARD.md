# Tableau Dashboard — Campaign Performance & Targeting

**🔗 Live:** https://public.tableau.com/app/profile/sivansh.satpathy/viz/Book1_17813492980260/Dashboard1

The dashboard is built on the extracts in `tableau/extracts/`
(regenerate them with `python src/export_tableau.py`).

**Data source:** connect `contacts_enriched.csv` as the primary source. The
small `agg_*.csv` files are optional pre-aggregated alternatives if Tableau
Public feels slow on the row-level file.

## Calculated fields

| Field | Formula |
|---|---|
| `Conversion Rate` | `SUM([converted]) / COUNT([converted])` (format: percentage, 1 dp) |
| `Contacts Display` | `IF [campaign] >= 8 THEN "8+" ELSE STR([campaign]) END` |
| `Prior Relationship` | `IF [poutcome] = "success" THEN "Previously converted" ELSEIF [poutcome] = "failure" THEN "Previously declined" ELSE "Never contacted" END` |

## Worksheets

1. **KPI tiles** — total contacts, conversions, `Conversion Rate`, avg contacts
   per client (`AVG([campaign])`). One sheet per tile, text mark only.
2. **Contact fatigue** — `Contacts Display` on columns; dual axis with
   `COUNT(contacts)` as bars and `Conversion Rate` as a line. Synchronise off,
   bars in light grey, line in red.
3. **Segment explorer** — `job` on rows sorted by `Conversion Rate` descending,
   bar chart; reference line at the dataset-average conversion rate. Add a
   dimension parameter (`job` / `age_band` / `education_group`) to make the
   sheet swappable.
4. **Customer history** — `Prior Relationship` bars with `Conversion Rate`
   labels; this is the headline chart, keep it on top.
5. **Channel × month** — `month_num`-sorted `month` on columns, `Conversion
   Rate` on rows, `contact` on colour; add `COUNT(contacts)` as a thin bar
   chart below on the dashboard so rate is never read without volume.

## Dashboard layout

- Size: 1300 × 800 (fits a laptop demo without scrolling).
- Top row: KPI tiles. Left column: customer history + segment explorer.
  Right column: contact fatigue + channel × month.
- Global filters: `month`, `contact`, `age_band` — applied to all sheets via
  "All Using This Data Source".
- Interactivity: use the segment explorer as a filter action so clicking a
  job filters the fatigue and timing charts.

Publish to Tableau Public and paste the link into the main README.
