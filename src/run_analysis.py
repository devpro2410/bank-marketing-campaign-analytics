"""Run every query in sql/ against the DuckDB database and export the results.

Each .sql file holds one self-contained business question; its result set is
written to outputs/tables/<name>.csv and echoed to the console.

Run:  python src/run_analysis.py        (after src/prepare_data.py)
"""

from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "bank_marketing.duckdb"
SQL_DIR = ROOT / "sql"
OUT_DIR = ROOT / "outputs" / "tables"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH), read_only=True)

    pd.set_option("display.width", 120)
    pd.set_option("display.max_rows", 60)

    for sql_file in sorted(SQL_DIR.glob("*.sql")):
        result = con.execute(sql_file.read_text()).df()
        out_csv = OUT_DIR / f"{sql_file.stem}.csv"
        result.to_csv(out_csv, index=False)

        print(f"\n{'=' * 78}\n{sql_file.name}  ->  {out_csv.relative_to(ROOT)}")
        print("-" * 78)
        print(result.to_string(index=False))

    con.close()


if __name__ == "__main__":
    main()
