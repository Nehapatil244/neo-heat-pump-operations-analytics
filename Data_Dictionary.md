# Data Dictionary

> **Simulated data.** Every record is synthetic, created for a portfolio case study. No real customers, prices or company results are included.

**Files:** `data/raw/raw_orders_export.csv` (163 rows, as received) → `data/processed/cleaned_orders.csv` (160 unique orders, validated inputs + derived columns).

**Grain:** one row = one customer order. **Period:** orders booked 1 Jan – 30 Jun 2026. **Report as-of date:** 30 Jun 2026.

## 1. Raw export columns

| Column | Type | Description | Example |
|---|---|---|---|
| Order ID | Text | Order reference as typed in the export (some have stray spaces) | `NHP-0042` |
| Order Date | Text date | Date the order was booked. Mostly DD-MM-YYYY; a few YYYY/MM/DD | `14-03-2026` |
| Customer Ref | Text | Anonymised customer code - no names, phones or addresses | `CUST-4657` |
| Customer Type | Text | Residential / Commercial / Institutional (some spelling variants) | `Commercial` |
| Region | Text | Delivery region band | `Bengaluru` |
| Product Category | Text | Product family ordered (some spelling variants) | `Heat Pump Dryer` |
| Units | Number | Number of machines on the order | `2` |
| Order Value (INR) | Text/number | Illustrative simulated value - NOT real pricing (a few blanks or 'Rs.' text) | `485000` |
| Expected Delivery | Text date | Delivery date promised to the customer | `28-03-2026` |
| Dispatch Date | Text date | Date the unit left the factory (blank = not yet dispatched) | `25-03-2026` |
| Delivery Date | Text date | Actual delivery date (blank = not yet delivered) | `27-03-2026` |
| Expected Installation | Text date | Installation date promised to the customer | `02-04-2026` |
| Installation Date | Text date | Actual installation/commissioning date (blank = not installed) | `01-04-2026` |
| Status | Text | Order status as typed (Completed / Pending / Cancelled plus variants) | `Completed` |
| Delivery Delay Reason | Text | Reason entered when delivery was late (often blank) | `Production backlog` |
| Installation Delay Reason | Text | Reason entered when installation was late (often blank) | `Customer site not ready` |
| Cancellation Reason | Text | Reason for cancelled orders | `Price / budget` |
| Notes | Text | Short operational note - no personal data | `Site survey done` |

## 2. Cleaned dataset columns

*Source* tells you where the column comes from: **Input** = validated value from the export, **Cleaning** = added by the cleaning step, **Formula** = calculated (Excel formula in the workbook, same rule in `dashboard/kpi_engine.py`).

| Column | Type | Source | Meaning | Rule / formula | Example |
|---|---|---|---|---|---|
| `Order_ID` | Text | Input | Unique order reference | Trimmed; duplicates removed | `NHP-0042` |
| `Order_Date` | Date | Input | Date the order was booked | Parsed to a real date | `14-Mar-2026` |
| `Customer_Ref` | Text | Input | Anonymised customer code | Unchanged | `CUST-4657` |
| `Customer_Type` | Text | Input | Residential / Commercial / Institutional | Spelling standardised | `Commercial` |
| `Region` | Text | Input | Bengaluru / Rest of Karnataka / Other States | Unchanged | `Bengaluru` |
| `Product_Category` | Text | Input | One of 5 standard product families | Spelling standardised | `Heat Pump Dryer` |
| `Units` | Number | Input | Machines on the order | Unchanged | `2` |
| `Order_Value_INR` | Number | Input | Simulated order value in rupees (illustrative only) | Text stripped; blanks kept blank | `485000` |
| `Expected_Delivery_Date` | Date | Input | Promised delivery date | Parsed | `28-Mar-2026` |
| `Dispatch_Date` | Date | Input | Date unit left the factory | Parsed; blank = not dispatched | `25-Mar-2026` |
| `Actual_Delivery_Date` | Date | Input | Actual delivery date | Parsed; invalid dates set blank and flagged | `27-Mar-2026` |
| `Expected_Installation_Date` | Date | Input | Promised installation date | Parsed | `02-Apr-2026` |
| `Actual_Installation_Date` | Date | Input | Actual installation date | Parsed; blank = not installed | `01-Apr-2026` |
| `Order_Status` | Text | Input | Completed (installed) / Pending (open) / Cancelled | Standardised; 'In Progress' -> Pending | `Completed` |
| `Delivery_Delay_Reason` | Text | Input | Recorded reason for a late delivery | Unchanged (blank = not recorded) | `Component shortage` |
| `Installation_Delay_Reason` | Text | Input | Recorded reason for a late installation | Unchanged | `Customer site not ready` |
| `Cancellation_Reason` | Text | Input | Recorded cancellation reason | Unchanged | `Long lead time` |
| `Operational_Notes` | Text | Input | Short operational note | Unchanged | `Site survey done` |
| `DQ_Flag` | Text | Cleaning | Data-quality issue found on the row, or OK | See DATA QUALITY LOG | `Installed before delivery` |
| `Valid_Dispatch_Timing` | 1/0 | Cleaning | 1 = dispatch date can be used for production/transit time | 0 if dispatch date is impossible | `1` |
| `Valid_Delivery_Timing` | 1/0 | Cleaning | 1 = delivery date can be used for delivery KPIs | 0 if delivery date invalid or order cancelled after delivery | `1` |
| `Valid_Install_Timing` | 1/0 | Cleaning | 1 = installation date can be used for installation KPIs | 0 if installed before delivery or date missing on a completed order | `1` |
| `Order_Month` | Date | Formula | First day of the order month (for trends) | DATE(YEAR(Order_Date),MONTH(Order_Date),1) | `01-Mar-2026` |
| `Delivery_Due` | 1/0 | Formula | Order was due for delivery by the report date | Not cancelled AND Expected_Delivery_Date <= As-of date | `1` |
| `Delivered` | 1/0 | Formula | Order has been delivered | Not cancelled AND (delivery date present OR status Completed) | `1` |
| `Delivery_Delay_Days` | Number | Formula | Actual minus promised delivery date (negative = early) | Only for delivered orders with valid dates; otherwise blank | `3` |
| `Delivery_Timeliness` | Text | Formula | Early / On Time / Late | From Delivery_Delay_Days (<0, =0, >0) | `Late` |
| `Install_Due` | 1/0 | Formula | Order was due for installation by the report date | Not cancelled AND Expected_Installation_Date <= As-of date | `1` |
| `Installed` | 1/0 | Formula | Order has been installed | Not cancelled AND (installation date present OR status Completed) | `1` |
| `Install_Delay_Days` | Number | Formula | Actual minus promised installation date | Only installed orders with valid dates | `-1` |
| `Install_Timeliness` | Text | Formula | Early / On Time / Late | From Install_Delay_Days | `Early` |
| `Production_Days` | Number | Formula | Order date to dispatch | Valid dispatch date, not cancelled | `11` |
| `Transit_Days` | Number | Formula | Dispatch to delivery | Valid dispatch and delivery dates | `2` |
| `Install_Lead_Days` | Number | Formula | Delivery to installation (installation duration) | Valid delivery and installation dates | `4` |
| `Order_To_Delivery_Days` | Number | Formula | Order date to delivery (fulfilment time) | Valid delivery date | `13` |
| `Order_Cycle_Days` | Number | Formula | Order date to installation (end-to-end) | Completed orders with valid installation date | `18` |
| `Current_Stage` | Text | Formula | Where the order is today | Cancelled / Completed / Awaiting Installation / In Transit / In Production | `In Transit` |
| `Overdue` | 1/0 | Formula | Open order past the promise for its current stage | Pending AND (not delivered and delivery promise passed, OR delivered and installation promise passed) | `0` |
| `Days_Overdue` | Number | Formula | Days past the promise for the current stage | As-of date minus the relevant promised date | `14` |
| `Overdue_Stage` | Text | Formula | Stage at which the overdue order is stuck | Delivery / Installation | `Installation` |

## 3. Workbook-only helper columns

| Column | Type | Source | Meaning | Rule | Example |
|---|---|---|---|---|---|
| `In_Dashboard_Filter` | 1/0 | Formula | 1 = row matches the dashboard filters | Used only by the OPERATIONS DASHBOARD | `1` |
| `Overdue_Rank_Key` | Number | Formula | Helper to list the most overdue orders on the dashboard | Days_Overdue + tiny row tie-breaker | `14.00042` |

## 4. Allowed values

- **Order_Status:** Completed (delivered **and** installed) · Pending (open) · Cancelled
- **Product_Category:** Heat Pump Water Heater · Commercial Heat Pump · Swimming Pool Heat Pump · Heat Pump Dryer · Custom Requirement
- **Customer_Type:** Residential · Commercial · Institutional
- **Region:** Bengaluru · Rest of Karnataka · Other States
- **Delivery_Delay_Reason:** Production backlog · Component shortage · Transport scheduling · Dispatch scheduling · blank (not recorded)
- **Installation_Delay_Reason:** Customer site not ready · Knock-on from late delivery · Technician availability · Installation scheduling · blank
- **Cancellation_Reason:** Customer postponed project · Price / budget · Long lead time
- **Current_Stage:** In Production · In Transit · Awaiting Installation · Completed · Cancelled

## 5. Source and limitations

- Generated by `scripts/01_generate_synthetic_data.py` (fixed random seed 42, so it is reproducible).
- Order values are illustrative ranges, **not** Neo Heat Pump price lists.
- `Customer_Ref` is a random code; there are no names, phone numbers or addresses anywhere in the project.
- There is no technician ID, cost, warranty/service or customer-satisfaction data, so those questions cannot be answered.
- Deliberately injected data problems are listed in `data/raw/injected_issues_reference.csv` for transparency.
