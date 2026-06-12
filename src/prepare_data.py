"""Clean the raw campaign extract and build the DuckDB analytical database.

Pipeline:
    data/raw/bank-additional-full.csv
        -> cleaning + feature engineering (pandas)
        -> data/bank_marketing.duckdb
               raw_contacts : untouched raw load (audit trail)
               contacts     : cleaned, enriched analysis table

Run:  python src/prepare_data.py
"""

from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_CSV = ROOT / "data" / "raw" / "bank-additional-full.csv"
DB_PATH = ROOT / "data" / "bank_marketing.duckdb"

# Dotted column names are awkward in SQL; rename once at ingestion.
RENAMES = {
    "emp.var.rate": "emp_var_rate",
    "cons.price.idx": "cons_price_idx",
    "cons.conf.idx": "cons_conf_idx",
    "euribor3m": "euribor_3m",
    "nr.employed": "nr_employed",
}

AGE_BINS = [0, 25, 35, 45, 55, 65, 200]
AGE_LABELS = ["<25", "25-34", "35-44", "45-54", "55-64", "65+"]

EDUCATION_GROUPS = {
    "basic.4y": "basic",
    "basic.6y": "basic",
    "basic.9y": "basic",
    "high.school": "high_school",
    "professional.course": "professional",
    "university.degree": "university",
    "illiterate": "basic",
    "unknown": "unknown",
}


def bucket_contacts(n: int) -> str:
    """Group the number of campaign contacts into reporting buckets."""
    if n <= 3:
        return str(n)
    if n <= 5:
        return "4-5"
    return "6+"


def clean(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.rename(columns=RENAMES).copy()

    before = len(df)
    df = df.drop_duplicates()
    print(f"Dropped {before - len(df)} exact duplicate rows ({before} -> {len(df)})")

    # Binary target for easy aggregation: AVG(converted) == conversion rate.
    df["converted"] = (df["y"] == "yes").astype("int8")

    # pdays uses 999 as a "never contacted before" sentinel. Keep the signal as a
    # flag and NULL the sentinel so day-counts aggregate correctly.
    df["previously_contacted"] = (df["pdays"] != 999).astype("int8")
    df["pdays"] = df["pdays"].where(df["pdays"] != 999)

    df["age_band"] = pd.cut(df["age"], bins=AGE_BINS, labels=AGE_LABELS, right=False)
    df["education_group"] = df["education"].map(EDUCATION_GROUPS)
    df["contact_bucket"] = df["campaign"].map(bucket_contacts)

    # Calendar ordering helpers for charts/dashboards (campaign has no January–
    # February or weekend contacts).
    month_order = ["mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    df["month_num"] = df["month"].map({m: i + 3 for i, m in enumerate(month_order)})
    df["weekday_num"] = df["day_of_week"].map(
        {"mon": 1, "tue": 2, "wed": 3, "thu": 4, "fri": 5}
    )

    return df


def main() -> None:
    raw = pd.read_csv(RAW_CSV, sep=";")
    print(f"Loaded {len(raw):,} rows x {raw.shape[1]} columns from {RAW_CSV.name}")

    contacts = clean(raw)

    con = duckdb.connect(str(DB_PATH))
    con.register("raw_df", raw)
    con.register("contacts_df", contacts)
    con.execute("CREATE OR REPLACE TABLE raw_contacts AS SELECT * FROM raw_df")
    con.execute("CREATE OR REPLACE TABLE contacts AS SELECT * FROM contacts_df")

    n, rate = con.execute(
        "SELECT COUNT(*), ROUND(100.0 * AVG(converted), 1) FROM contacts"
    ).fetchone()
    print(f"Built {DB_PATH.name}: contacts table = {n:,} rows, "
          f"overall conversion = {rate}%")
    con.close()


if __name__ == "__main__":
    main()
