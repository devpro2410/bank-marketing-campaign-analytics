"""Download the UCI Bank Marketing dataset into data/raw/.

The raw CSV is committed to the repo for reproducibility, so this script is only
needed if you want to re-fetch it from scratch.
"""

import io
import urllib.request
import zipfile
from pathlib import Path

UCI_ZIP_URL = "https://archive.ics.uci.edu/static/public/222/bank+marketing.zip"
RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
TARGET = RAW_DIR / "bank-additional-full.csv"


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if TARGET.exists():
        print(f"Already present: {TARGET}")
        return

    print(f"Downloading {UCI_ZIP_URL} ...")
    with urllib.request.urlopen(UCI_ZIP_URL) as resp:
        outer = zipfile.ZipFile(io.BytesIO(resp.read()))

    # The UCI archive nests a second zip: bank-additional.zip
    inner_bytes = outer.read("bank-additional.zip")
    inner = zipfile.ZipFile(io.BytesIO(inner_bytes))
    csv_bytes = inner.read("bank-additional/bank-additional-full.csv")

    TARGET.write_bytes(csv_bytes)
    print(f"Saved {TARGET} ({len(csv_bytes) / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
