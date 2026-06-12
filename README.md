# Bank Marketing Campaign Analytics

Analysis of **41,188 outbound telemarketing contacts** from a Portuguese retail
bank's term-deposit campaign (May 2008 – Nov 2010), quantifying how customer
history, contact frequency and channel engagement drove conversion — and what
the bank should change in its next campaign.

**Stack:** Python (pandas) for ingestion and cleaning · DuckDB as a local
analytical warehouse · SQL for the analysis layer · Tableau for the dashboard
· matplotlib/seaborn for report figures.

## Headline findings

| Finding | Evidence |
|---|---|
| **Customer history is the strongest signal.** Clients who converted in a previous campaign convert again at **65%** — ~6x the 11.3% baseline — yet they were only 3.3% of the call list. | `sql/04_customer_history.sql` |
| **Repeated outreach destroys conversion.** First contacts convert at **13.0%**; by the 7th attempt the rate is **6.0%**, and ~4% beyond that. Clients requiring 4+ contacts absorbed **48% of all dials** but yielded only **12% of conversions**. | `sql/03_contact_frequency.sql` |
| **Students (31%) and retirees (25%)** convert at 2–3x the average; conversion is U-shaped in age while the over-targeted 35–54 core sits *below* average. | `sql/02_conversion_by_segment.sql` |
| **Cellular converts at ~3x landline** (14.7% vs 5.2%), consistently across every month of the campaign. | `sql/05_channel_and_timing.sql` |

### Contact fatigue
![Contact fatigue](outputs/figures/01_contact_fatigue.png)

### Customer history
![Customer history](outputs/figures/02_customer_history.png)

### Segments
![Segment conversion](outputs/figures/03_segment_conversion.png)

### Channel & timing
![Channel by month](outputs/figures/04_channel_by_month.png)

## Recommendations

1. **Lead with history, not demographics.** Build the next call list starting
   from prior converters and recent prior contacts (50–66% conversion), then
   high-affinity segments (students, retirees), and only then cold names.
2. **Cap contact attempts at ~3 per client.** The fatigue curve is monotonic;
   redirect the ~27% of dials currently spent on 4th-and-later attempts toward
   fresh leads. (Observational data, so the decay isn't strictly causal — but the
   near-zero incremental yield justifies the cap operationally either way.)
3. **Prioritise mobile numbers** in dialler queues and invest in mobile-number
   acquisition for the landline-only book.
4. **Smooth the calendar.** May's volume blast converted worst (3–11%);
   low-volume months converted at 40%+. Spread volume and protect list quality
   over hitting monthly dial quotas.

## Repository structure

```
├── data/
│   ├── raw/bank-additional-full.csv   # source extract (UCI)
│   └── README.md                      # data dictionary + quality notes
├── notebooks/
│   └── 01_exploratory_analysis.ipynb  # executed EDA walkthrough
├── sql/                               # analysis layer, one question per file
├── src/
│   ├── download_data.py               # (re)fetch the raw extract
│   ├── prepare_data.py                # clean + build DuckDB warehouse
│   ├── run_analysis.py                # run sql/ -> outputs/tables/
│   ├── make_charts.py                 # report figures
│   └── export_tableau.py              # dashboard extracts
├── outputs/
│   ├── figures/                       # report charts (PNG)
│   └── tables/                        # query results (CSV)
└── tableau/
    ├── extracts/                      # Tableau-ready data
    └── DASHBOARD.md                   # dashboard design & build notes
```

## Reproducing the analysis

```bash
pip install -r requirements.txt
python src/prepare_data.py     # clean data, build data/bank_marketing.duckdb
python src/run_analysis.py     # run all SQL, export result tables
python src/make_charts.py      # regenerate figures
python src/export_tableau.py   # regenerate Tableau extracts
```

## Methodology notes

- **Duplicates:** 12 exact duplicate rows dropped (41,188 → 41,176 unique
  contacts).
- **Sentinel handling:** `pdays = 999` ("never previously contacted") is
  converted to `NULL` plus an explicit `previously_contacted` flag.
- **Leakage:** `duration` (call length) is only known after a call finishes,
  so it is excluded from all targeting recommendations — using it would
  overstate how well outcomes can be anticipated before dialling.
- **`unknown` categories** are reported as-is rather than imputed.

## Data source

[Bank Marketing dataset](https://archive.ics.uci.edu/dataset/222/bank+marketing),
UCI Machine Learning Repository (CC BY 4.0).

> S. Moro, P. Cortez and P. Rita. *A Data-Driven Approach to Predict the
> Success of Bank Telemarketing.* Decision Support Systems, Elsevier, 62:22-31,
> June 2014.
