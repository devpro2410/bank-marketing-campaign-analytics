"""Generate the report figures used in the README from the DuckDB database.

Run:  python src/make_charts.py         (after src/prepare_data.py)
"""

from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "bank_marketing.duckdb"
FIG_DIR = ROOT / "outputs" / "figures"

ACCENT = "#1f6f8b"
MUTED = "#c9d6df"
WARN = "#d1495b"


def style():
    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams.update({
        "figure.dpi": 130,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.spines.top": False,
        "axes.spines.right": False,
    })


def save(fig, name: str) -> None:
    path = FIG_DIR / name
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {path.relative_to(ROOT)}")


def fig_contact_fatigue(con) -> None:
    df = con.execute("""
        SELECT LEAST(campaign, 8) AS n_contacts,
               COUNT(*) AS clients,
               100.0 * AVG(converted) AS rate
        FROM contacts GROUP BY 1 ORDER BY 1
    """).df()
    labels = [str(int(n)) if n < 8 else "8+" for n in df["n_contacts"]]

    fig, ax1 = plt.subplots(figsize=(8, 4.5))
    ax1.bar(labels, df["clients"], color=MUTED, label="Clients contacted")
    ax1.set_ylabel("Clients")
    ax1.set_xlabel("Number of contacts during the campaign")

    ax2 = ax1.twinx()
    ax2.plot(labels, df["rate"], color=WARN, marker="o", linewidth=2.2,
             label="Conversion rate")
    for x, r in zip(labels, df["rate"]):
        ax2.annotate(f"{r:.1f}%", (x, r), textcoords="offset points",
                     xytext=(0, 9), ha="center", fontsize=9, color=WARN)
    ax2.set_ylabel("Conversion rate (%)")
    ax2.set_ylim(0, 16)
    ax2.grid(False)
    ax2.spines["right"].set_visible(True)

    ax1.set_title("Contact fatigue: each additional call converts worse")
    save(fig, "01_contact_fatigue.png")


def fig_customer_history(con) -> None:
    df = con.execute("""
        SELECT poutcome, COUNT(*) AS n, 100.0 * AVG(converted) AS rate
        FROM contacts GROUP BY 1 ORDER BY rate
    """).df()
    labels = {
        "success": "Converted in a\nprevious campaign",
        "failure": "Contacted before,\ndid not convert",
        "nonexistent": "Never contacted\nbefore",
    }
    df["label"] = df["poutcome"].map(labels)

    fig, ax = plt.subplots(figsize=(8, 4))
    colors = [ACCENT if p == "success" else MUTED for p in df["poutcome"]]
    ax.barh(df["label"], df["rate"], color=colors)
    for i, (rate, n) in enumerate(zip(df["rate"], df["n"])):
        ax.text(rate + 0.8, i, f"{rate:.1f}%  (n={n:,})", va="center", fontsize=10)
    ax.set_xlim(0, 78)
    ax.set_xlabel("Conversion rate (%)")
    ax.set_title("Customer history is the strongest predictor of conversion")
    save(fig, "02_customer_history.png")


def fig_segments(con) -> None:
    df = con.execute("""
        SELECT job, COUNT(*) AS n, 100.0 * AVG(converted) AS rate
        FROM contacts GROUP BY 1 ORDER BY rate DESC
    """).df()

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = [ACCENT if r >= 20 else MUTED for r in df["rate"]]
    ax.barh(df["job"], df["rate"], color=colors)
    overall = con.execute("SELECT 100.0 * AVG(converted) FROM contacts").fetchone()[0]
    ax.axvline(overall, color=WARN, linestyle="--", linewidth=1.2)
    ax.annotate(f"campaign avg {overall:.1f}%", (overall + 0.4, len(df) - 1.2),
                color=WARN, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Conversion rate (%)")
    ax.set_title("Students and retirees convert at 2-3x the campaign average")
    save(fig, "03_segment_conversion.png")


def fig_channel_month(con) -> None:
    df = con.execute("""
        SELECT month_num, UPPER(month[1]) || month[2:] AS month,
               contact, COUNT(*) AS n, 100.0 * AVG(converted) AS rate
        FROM contacts GROUP BY 1, 2, 3 ORDER BY 1
    """).df()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.5, 6), sharex=True,
                                   height_ratios=[2, 1])
    for channel, color in [("cellular", ACCENT), ("telephone", "#9a8c98")]:
        sub = df[df["contact"] == channel]
        ax1.plot(sub["month"], sub["rate"], marker="o", color=color, label=channel)
    ax1.set_ylabel("Conversion rate (%)")
    ax1.legend(title="Channel", frameon=False)
    ax1.set_title("Cellular outperforms landline in every month of the campaign")

    vol = df.pivot_table(index="month", columns="contact", values="n",
                         sort=False).fillna(0)
    ax2.bar(vol.index, vol["cellular"], color=ACCENT, label="cellular")
    ax2.bar(vol.index, vol["telephone"], bottom=vol["cellular"],
            color="#9a8c98", label="telephone")
    ax2.set_ylabel("Contacts")
    save(fig, "04_channel_by_month.png")


def main() -> None:
    style()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH), read_only=True)
    fig_contact_fatigue(con)
    fig_customer_history(con)
    fig_segments(con)
    fig_channel_month(con)
    con.close()


if __name__ == "__main__":
    main()
