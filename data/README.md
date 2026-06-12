# Data Dictionary

Source: **Bank Marketing (with social/economic context)** dataset, UCI Machine Learning
Repository — direct telemarketing campaigns of a Portuguese retail bank (May 2008 – Nov 2010).
File used: `bank-additional-full.csv` (41,188 contacts, 20 input variables, `;`-separated).

> S. Moro, P. Cortez and P. Rita. *A Data-Driven Approach to Predict the Success of Bank
> Telemarketing.* Decision Support Systems, Elsevier, 62:22-31, June 2014.

## Client attributes

| Column | Type | Description |
|---|---|---|
| `age` | int | Client age in years |
| `job` | cat | Job type (admin., blue-collar, student, retired, ...) |
| `marital` | cat | Marital status (`divorced` includes widowed) |
| `education` | cat | Education level (`basic.4y` / `basic.6y` / `basic.9y` / `high.school` / ...) |
| `default` | cat | Has credit in default? (yes / no / unknown) |
| `housing` | cat | Has a housing loan? |
| `loan` | cat | Has a personal loan? |

## Current-campaign attributes

| Column | Type | Description |
|---|---|---|
| `contact` | cat | Contact channel: `cellular` or `telephone` (landline) |
| `month` | cat | Month of the last contact |
| `day_of_week` | cat | Weekday of the last contact (mon–fri) |
| `duration` | int | Last-call duration in seconds — **leaky feature**, see note below |
| `campaign` | int | Number of contacts made to this client during this campaign |

## Customer-history attributes

| Column | Type | Description |
|---|---|---|
| `pdays` | int | Days since the client was last contacted in a previous campaign; **999 = never contacted** |
| `previous` | int | Number of contacts before this campaign |
| `poutcome` | cat | Outcome of the previous campaign (success / failure / nonexistent) |

## Social & economic context (quarterly/monthly indicators)

| Column | Type | Description |
|---|---|---|
| `emp.var.rate` | float | Employment variation rate |
| `cons.price.idx` | float | Consumer price index |
| `cons.conf.idx` | float | Consumer confidence index |
| `euribor3m` | float | Euribor 3-month rate |
| `nr.employed` | float | Number of employees (thousands) |

## Target

| Column | Type | Description |
|---|---|---|
| `y` | cat | Did the client subscribe to a term deposit? (yes / no) |

## Notes & quality issues handled in `src/prepare_data.py`

- **12 exact duplicate rows** are dropped (41,188 → 41,176 unique contacts).
- **`pdays = 999`** is a sentinel meaning "never previously contacted"; it is converted to
  `NULL` plus an explicit `previously_contacted` flag so averages aren't distorted.
- **`duration`** is only known *after* a call ends, so it cannot inform targeting decisions.
  It is kept for descriptive analysis but excluded from all recommendation logic.
- Several categoricals contain an explicit `unknown` level; these are kept as-is and
  reported, not imputed.
