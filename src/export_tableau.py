"""Export Tableau-ready extracts to tableau/extracts/.

Two kinds of extracts are produced:
  contacts_enriched.csv  - the full cleaned row-level table, for free-form
                           exploration and the dashboard's detail views
  agg_*.csv              - small pre-aggregated cuts that back the headline
                           dashboard tiles (fast to load on Tableau Public)

Run:  python src/export_tableau.py      (after src/prepare_data.py)
"""

from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "bank_marketing.duckdb"
OUT_DIR = ROOT / "tableau" / "extracts"

AGGREGATES = {
    "agg_contact_frequency": """
        SELECT LEAST(campaign, 10) AS n_contacts,
               COUNT(*) AS clients,
               SUM(converted) AS conversions,
               ROUND(100.0 * AVG(converted), 2) AS conversion_rate_pct
        FROM contacts GROUP BY 1 ORDER BY 1
    """,
    "agg_segments": """
        SELECT 'job' AS dimension, job AS segment,
               COUNT(*) AS contacts, SUM(converted) AS conversions,
               ROUND(100.0 * AVG(converted), 2) AS conversion_rate_pct
        FROM contacts GROUP BY job
        UNION ALL
        SELECT 'age_band', age_band::VARCHAR, COUNT(*), SUM(converted),
               ROUND(100.0 * AVG(converted), 2)
        FROM contacts GROUP BY age_band
        UNION ALL
        SELECT 'previous_outcome', poutcome, COUNT(*), SUM(converted),
               ROUND(100.0 * AVG(converted), 2)
        FROM contacts GROUP BY poutcome
        ORDER BY 1, 5 DESC
    """,
    "agg_month_channel": """
        SELECT month_num, month, contact AS channel,
               COUNT(*) AS contacts, SUM(converted) AS conversions,
               ROUND(100.0 * AVG(converted), 2) AS conversion_rate_pct
        FROM contacts GROUP BY 1, 2, 3 ORDER BY 1, 3
    """,
}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH), read_only=True)

    row_level = OUT_DIR / "contacts_enriched.csv"
    con.execute(f"COPY contacts TO '{row_level}' (HEADER, DELIMITER ',')")
    print(f"Wrote {row_level.relative_to(ROOT)}")

    for name, query in AGGREGATES.items():
        out = OUT_DIR / f"{name}.csv"
        con.execute(query).df().to_csv(out, index=False)
        print(f"Wrote {out.relative_to(ROOT)}")

    con.close()


if __name__ == "__main__":
    main()
