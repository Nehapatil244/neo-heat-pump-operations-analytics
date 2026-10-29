# Data Quality Report

> **Simulated data.** The raw export is synthetic. Its data-entry problems were **deliberately injected** to imitate a real manual export, and they are listed openly in [`data/raw/injected_issues_reference.csv`](../data/raw/injected_issues_reference.csv).

| Item | Value |
|---|---|
| Input | [`data/raw/raw_orders_export.csv`](../data/raw/raw_orders_export.csv): 163 rows, all values stored as text |
| Output | [`data/processed/cleaned_orders.csv`](../data/processed/cleaned_orders.csv): 160 unique orders |
| Change log | [`data/processed/cleaning_log.csv`](../data/processed/cleaning_log.csv): 48 entries, one per changed or flagged value |
| Cleaning script | [`scripts/02_clean_data.py`](../scripts/02_clean_data.py) |
| Excel view | `RAW DATA` (untouched), `CLEANED DATA`, `DATA QUALITY LOG` (live checks, rules and the full log) |

**Guiding principle:** never silently change business information. Every change follows a written rule and appears in the log. When a value cannot be trusted, the row is kept, flagged, and excluded **only from the metric it would distort**.

## 1. Issues found

| # | Check | Found | What was done | Rule |
|---|---|---|---|---|
| 1 | Exact duplicate rows (double export) | 3 rows | Second copy removed | R2 |
| 2 | Spaces around Order IDs | 4 | Trimmed | R1 |
| 3 | Duplicate Order IDs after removing duplicates | 0 | — | — |
| 4 | Status spelling variants (`completed`, `Complete`, `COMPLETED`, `PENDING`, `pending `, `In Progress`, `Canceled`) | 12 | Mapped to Completed / Pending / Cancelled (`In Progress` → Pending) | R3 |
| 5 | Category variants (`Pool Heat Pump`, `HP Water Heater`, `commercial heat pump`) | 8 | Mapped to the 5 standard names | R3 |
| 6 | Customer-type variants (`residential`, `Comm.`) | 4 | Mapped to standard names | R3 |
| 7 | Dates in a second format (`YYYY/MM/DD`) | 6 | Converted to real dates | R4 |
| 8 | Impossible calendar date (`31-02-2026`) in a delivery date | 1 | Set blank and flagged; excluded from delivery timing (the order is still counted as Completed) | R4 |
| 9 | Order value typed as text (`Rs. 216,000`) | 2 | Text and separators removed | R5 |
| 10 | Order value missing | 3 | Kept blank; excluded from value KPIs only | R5 |
| 11 | Installation date earlier than delivery date | 2 | **Dates not changed**; excluded from installation timing | R6 |
| 12 | Dispatch date earlier than order date | 1 | **Date not changed**; excluded from production and transit time | R6 |
| 13 | Completed order with no installation date | 1 | Status kept (system of record); excluded from installation timing; flagged for confirmation | R7 |
| 14 | Cancelled order with a delivery date (unit returned) | 1 | Kept as Cancelled; excluded from delivery KPIs; **not** treated as a delivery failure | R8 |
| 15 | Late deliveries with no reason recorded | 8 of 37 | Left blank (never invented); reported as a gap | R9 |
| 16 | Late installations with no reason recorded | 14 of 47 | Left blank; reported as a gap | R9 |
| 17 | Promised dates after the report date | various | Treated as *not yet due*, never overdue | R10 |
| 18 | Negative durations used in any KPI | 0 | Validation check passes | — |
| 19 | Pending orders counted as installed | 0 | Validation check passes | — |

**Result:** 151 of 160 rows are fully clean. 9 rows carry a `DQ_Flag`:
- 3 with a missing value;
- 2 installed before delivery;
- 1 invalid date;
- 1 dispatched before the order date;
- 1 completed order with no installation date;
- 1 returned unit.

## 2. Cleaning rules

| Rule | Situation | Action | Why |
|---|---|---|---|
| R1 | Spaces around IDs | Trim | Avoids false duplicates and failed lookups |
| R2 | Exact duplicate rows | Keep the first copy | Each order is counted once |
| R3 | Spelling variants | Map to one standard label | `COUNTIFS` needs exact labels |
| R4 | Text and mixed-format dates | Convert; set impossible dates blank and flag them | Dates are never guessed |
| R5 | Values as text or blank | Strip the text; leave blanks blank | Value KPIs exclude blanks only |
| R6 | Impossible date sequence | Keep the original; exclude it from the affected metric | Business data is not overwritten until the owner confirms it |
| R7 | Completed but no installation date | Keep the status; exclude from installation timing | Completion cannot be timed without a date |
| R8 | Cancelled after delivery | Keep as Cancelled; exclude from delivery KPIs | A cancellation is not a delivery failure |
| R9 | Late record with no reason | Leave blank and report it | Reasons are never invented |
| R10 | Promise after the as-of date | Treat as not yet due | A future promise cannot be broken yet |

## 3. Validation checks after cleaning

These checks run as live formulas on the `DATA QUALITY LOG` sheet, and all pass:

- 160 unique orders and 0 duplicate IDs.
- 0 status values outside Completed / Pending / Cancelled.
- 0 category values outside the standard list.
- 0 missing order dates.
- 0 pending orders counted as installed.
- 0 cancelled orders inside delivery timing KPIs.
- 0 negative production, transit or installation durations used.
- 0 orders flagged overdue whose promise is after the as-of date.

The independent reconciliation in [`scripts/05_qa_checks.py`](../scripts/05_qa_checks.py) confirms that 175 workbook values match Python with 0 differences. It also recounts the headline totals directly from the raw CSV.

## 4. Remaining limitations

- The 3 rows with impossible sequences need confirmation from the data owner. Until then they are excluded from timing KPIs, which slightly reduces sample sizes (134 timed deliveries and 118 timed installations).
- The missing reasons (8 delivery, 14 installation) limit root-cause analysis.
- There is no installation *booking* date, so "scheduled" means "has a promised installation date".
- The data is simulated, so its quality problems are illustrative, not an audit of real company records.

## 5. Recommendations to prevent these issues at source

1. Use dropdown lists for status, category, customer type and reason. This removes issues 4–6 and 15–16.
2. Use real date fields with validation (installation ≥ delivery ≥ dispatch ≥ order). This removes issues 7, 8, 11 and 12.
3. Make Order ID a unique key and block duplicate imports. This removes issues 1–3.
4. Make the order value numeric and required.
