# Project Methodology

## 1. Workflow

```
Raw export (163 rows, text)  ──►  Cleaning & validation  ──►  Cleaned dataset (160 orders)
   data/raw/                       scripts/02_clean_data.py      data/processed/cleaned_orders.csv
                                   + cleaning_log.csv (48)               │
                                                                         ▼
                    Derived columns (delays, stage durations, current stage, overdue flags)
                    same rules in Excel formulas and dashboard/kpi_engine.py
                                                                         │
                ┌────────────────────────────┬───────────────────────────┴───────────────┐
                ▼                            ▼                                            ▼
     Excel workbook (primary)       Streamlit dashboard                    Reports & case study
     excel/operations_analysis.xlsx dashboard/app.py                       reports/, analysis/
                │                            │
                └──────────► Independent QA: scripts/05_qa_checks.py (175 checks, 0 differences)
```

| Step | What happens | Script | Output |
|---|---|---|---|
| 1 | Generate the synthetic raw export, with deliberate data-entry problems | `01_generate_synthetic_data.py` | `data/raw/raw_orders_export.csv` |
| 2 | Clean, standardise and validate; log every change | `02_clean_data.py` | `cleaned_orders.csv`, `cleaning_log.csv`, `data_quality_checks.csv` |
| 3 | Calculate all KPIs and summaries independently in Python | `03_compute_results.py` | `analysis/results.json` |
| 4 | Build the Excel workbook with live formulas, charts and filters | `04_build_workbook.py` | `excel/operations_analysis.xlsx` |
| 5 | Recalculate the workbook (LibreOffice), then reconcile every KPI with Python | `05_qa_checks.py` | pass / fail report |
| 6–7 | Render the workbook previews and dashboard screenshots | `06_…`, `07_…` | `screenshots/` |
| 8 | Write the data dictionary from a single source | `08_write_data_dictionary.py` | `reports/Data_Dictionary.md` |
| 9 | Build the PDF case study | `09_build_case_study_pdf.py` | `reports/Case_Study.pdf` |

You do **not** need to run any script to use the project. The Excel file, CSVs, screenshots and PDF are already built. The scripts are there so anyone can see exactly how each output was produced.

## 2. Process model

Each order moves through these stages:

**Order booked → Production → Dispatch → Delivery → Installation (= Completed)**

- **Promises:** there are two customer-facing promised dates, an *expected delivery* date and an *expected installation* date.
- **Order status** is the system-of-record value: Completed, Pending or Cancelled.
- **Current stage** is derived from the dates: In Production, In Transit, Awaiting Installation, Completed or Cancelled.
- **Overdue** is judged against the promise for the order's current stage, at a fixed **as-of date (30 Jun 2026)**, never against "today".

## 3. Synthetic data design

- **Size and period:** 160 orders between Jan and Jun 2026.
- **Mix:** 5 product families, 3 customer types and 3 region bands.
- **Reproducible:** a fixed random seed (42) means the same dataset is generated every time.

**Assumptions built into the generator.** These are illustrations of the method, not discoveries about the business:

| Assumption | Why it is realistic |
|---|---|
| Custom, dryer and commercial units take longer and less predictably to build than standard water heaters | Engineered-to-order products have longer lead times |
| Some orders hit component shortages | Common for made-to-order equipment |
| Orders outside Karnataka spend longer in transit | Distance |
| Some installations wait for the customer's site to be ready | Civil, electrical and plumbing dependencies |
| Pool heat pump orders peak in Feb–Apr | Seasonal demand (assumed) |
| About 6% of orders are cancelled, each with a reason | Typical small share |
| About 25% of late records have no reason entered | Typical manual-entry gap |

**Deliberately injected data problems:** 47 issues, listed in `data/raw/injected_issues_reference.csv`. See the [Data Quality Report](../analysis/Data_Quality_Report.md).

## 4. KPI design principles

1. **Explicit denominators.** Every rate states exactly which records are counted.
2. **Separate four similar-sounding rates.** Order completion, delivery completion, on-time delivery and installation completion each answer a different question.
3. **Cancelled ≠ failure.** Cancelled orders are excluded from delivery and installation KPIs.
4. **Not due ≠ overdue.** A promise after the as-of date is never late.
5. **Exclude, don't overwrite.** A row with an impossible date is kept, but left out of the one metric it would distort.
6. **Reconcile.** Status counts must add up, and every workbook KPI must match the independent Python result.

## 5. Tools and why

| Tool | Used for | Why this tool |
|---|---|---|
| **Microsoft Excel** (primary deliverable) | KPI formulas, summary tables, filterable dashboard, documentation sheets | The standard tool for operations and MIS reporting roles |
| **Python (pandas)** | Generating, cleaning and validating the data; independent KPI recalculation | Repeatable cleaning with a full audit trail |
| **openpyxl + LibreOffice** | Writing and recalculating the workbook | Builds formulas and charts programmatically, then verifies they evaluate |
| **Streamlit + Plotly** | Browser dashboard | Easy to run, free to host, readable code |
| **Git and GitHub** | Version control and portfolio hosting | Recruiters can see the work |

**Not used:** Power BI. It needs Windows or a paid service to publish. The Excel dashboard and Streamlit app cover the same skills, and Power BI is listed as a future improvement.

## 6. Version history: audit of the starter workbook

An earlier workbook (v1, 40 simulated orders) was audited before this version was built.

**Kept from v1:**
- the `NHP-` order-ID convention and the product categories;
- the row-level data-check idea;
- "evidence type" labels on findings (observed versus hypothesis);
- the proposals-only action plan and its success metrics;
- the principle of never replacing missing dates with today's date.

**Changed, because v1 could not answer parts of the brief:**

| v1 limitation | Fix in v2 |
|---|---|
| "Completed" meant delivered **and** installed, so installation completion was 100% by definition | Separate promised installation date, plus Delivered and Installed flags |
| No installation promise date, so installation delay could not be measured | Expected installation date added |
| The data had zero quality issues, so there was nothing to clean | A raw export with documented problems, and a cleaning log |
| No order value, customer reference or dispatch date | Added (synthetic) |
| "Today" was the latest date in the data, which made pending orders look about 80 days overdue | A fixed, editable as-of date; promises after that date are "not yet due" |
| 40 rows | 160 orders, as the brief asks for 100–200 |

v1 is not included in the repository, because its numbers come from a different dataset and would conflict with v2.

## 7. Limitations of the method

- **Data:** the data is simulated; see the [Executive Summary](../reports/Executive_Summary.md#6-limitations).
- **Excel features:** openpyxl cannot create real PivotTables or slicers. The workbook uses formula-based summaries and dropdown filters instead, and the PIVOT ANALYSIS sheet explains how to add a real PivotTable and slicer in about 2 minutes.
- **Testing:** the workbook was recalculated and tested in LibreOffice, not in Microsoft Excel. It uses only functions supported by Excel 2010 and later (COUNTIFS, SUMIFS, AVERAGEIFS, INDEX/MATCH, LARGE, SUMPRODUCT). When you first open it in Excel, press **Ctrl+Alt+F9** to force a full recalculation.
