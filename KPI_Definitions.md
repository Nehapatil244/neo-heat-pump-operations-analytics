# KPI Definitions

> **Simulated data.** The results below come from 160 synthetic orders (Jan–Jun 2026) built for a portfolio case study. They are **not** real company performance.

**Report as-of date:** 30 Jun 2026. Anything promised after this date is *not yet due*. It is never counted as overdue.
**Where to find the formulas:** Excel `KPI ANALYSIS` sheet (column C), and the same rules in [`dashboard/kpi_engine.py`](../dashboard/kpi_engine.py).
**Reconciliation:** [`scripts/05_qa_checks.py`](../scripts/05_qa_checks.py) recomputes every KPI in Python and compares it with the recalculated workbook. It runs 175 checks and finds 0 differences.

## Four rates that are easy to confuse

| Rate | Question it answers | Numerator ÷ Denominator | Result |
|---|---|---|---|
| **Order completion rate** | How many committed orders are fully closed? | Completed ÷ non-cancelled orders | **80.1%** (121 ÷ 151) |
| **Delivery completion rate** | Did the deliveries that were due actually happen? | Due & delivered ÷ deliveries due | **98.5%** (130 ÷ 132) |
| **On-time delivery rate** | Were deliveries on or before the promised date? | On-time deliveries ÷ deliveries with valid dates | **72.4%** (97 ÷ 134) |
| **Installation completion rate** | Did the installations that were due actually happen? | Due & installed ÷ installations due | **93.6%** (117 ÷ 125) |

Deliveries almost always *happen* (98.5%), but about 1 in 4 is *late* (72.4% on time). These are different problems, so they need separate measures.

---

## A. Order management

### 1. Total Orders: **160**
- **Business meaning:** the workload booked in the period.
- **Formula:** `COUNTA(Order_ID)`. The numerator is the number of unique Order IDs; there is no denominator.
- **Applicable records:** all cleaned orders.
- **Exclusions:** the 3 exact duplicate rows in the raw export, which were removed.
- **Interpretation:** 160 orders were booked between Jan and Jun 2026, rising from 13 in January to 40 in May.
- **Limitation:** an order with several machines counts once (see `Units`).

### 2. Completed Orders: **121**
- **Business meaning:** orders that are fully delivered *and* installed.
- **Formula:** `COUNTIF(Order_Status,"Completed")`.
- **Applicable records:** Status = Completed.
- **Exclusions:** none.
- **Interpretation:** about three quarters of all orders are closed.
- **Limitation:** one Completed order has no installation date. Its status is kept as recorded, but it is flagged.

### 3. Pending Orders: **30**
- **Business meaning:** open orders still being worked on.
- **Formula:** `COUNTIF(Order_Status,"Pending")`.
- **Applicable records:** Status = Pending, including the raw value "In Progress", which was standardised to Pending.
- **Exclusions:** none.
- **Interpretation:** 21 of the 30 come from June orders, many of which are not yet due.
- **Limitation:** Pending is not the same as late. See Overdue Orders (KPI 16).

### 4. Cancelled Orders: **9**
- **Business meaning:** lost or withdrawn orders.
- **Formula:** `COUNTIF(Order_Status,"Cancelled")`.
- **Applicable records:** Status = Cancelled.
- **Exclusions:** none.
- **Interpretation:** the cancellation rate is 5.6% (9 ÷ 160), and every cancellation has a recorded reason.
- **Limitation:** cancelled orders are excluded from all delivery and installation KPIs. One unit that was delivered and then returned is **not** counted as a delivery failure.

**Reconciliation:** 121 + 30 + 9 = 160. The workbook shows "OK – statuses add up".

### 5. Order Completion Rate: **80.1%**
- **Formula:** Completed ÷ (Total − Cancelled), so the numerator is 121 and the denominator is 151.
- **Applicable records:** non-cancelled orders.
- **Exclusions:** cancelled orders, because they can never be completed.
- **Interpretation:** the figure is reasonable for a period whose last month is still in progress. By month it is 100% for January and 32% for June. The low June figure is a timing effect, not poor performance.
- **Limitation:** read it together with Overdue Orders. A low completion rate is only a problem when the open orders are past their promise.

### 6. Current Order Backlog: **30 orders, ₹2.74 crore (simulated)**
- **Business meaning:** open work still to deliver and/or install.
- **Formula:** `COUNTIF(Status,"Pending")` for the count and `SUMIFS(Order_Value,Status,"Pending")` for the value.
- **Where the backlog sits:** 14 orders are in production, 2 are in transit and 14 are delivered but awaiting installation.
- **Interpretation:** half of the backlog has already been delivered and is waiting for installation.
- **Limitation:** the order values are illustrative.

## B. Delivery performance

### 7. Total Deliveries Due: **132**
- **Formula:** non-cancelled orders where `Expected_Delivery_Date <= as-of date`.
- **Exclusions:** cancelled orders, and orders promised after 30 Jun 2026 (not yet due).
- **Companion KPI:** 130 of the 132 due deliveries have been made, a **delivery completion rate of 98.5%**.

### 8. On-Time Delivery Rate: **72.4%**
- **Business meaning:** the reliability of delivery promises.
- **Formula:** On-time deliveries ÷ deliveries with valid timing. The numerator is 97 (Delay Days ≤ 0, meaning early or on the day). The denominator is 134.
- **Applicable records:** delivered, non-cancelled orders with a valid promised date and a valid actual delivery date.
- **Exclusions:**
  - undelivered orders, which are neither on time nor late yet;
  - cancelled orders;
  - one order whose delivery date was an impossible date (31-02-2026).
- **Interpretation:** about 1 in 4 deliveries missed the promise.
- **Limitation:** delivering 1 day late counts the same as delivering 60 days late, so read this rate alongside the average delay.

### 9. Delayed Delivery Count: **37**
- **Formula:** `COUNTIF(Delivery_Delay_Days,">0")`, using the same records as KPI 8.
- **Interpretation:** 23 of the 37 late deliveries are Commercial Heat Pumps or Custom Requirements.

### 10. Average Delivery Delay: **6.7 days (late orders only)**
- **Formula:** `AVERAGEIF(Delivery_Delay_Days,">0")`.
- **Companion measures:**
  - average variance across all timed deliveries: **−1.5 days**, meaning that on average deliveries arrive slightly early;
  - maximum delay: **60 days**.
- **Interpretation:** most deliveries are early or on time. The problem is concentrated in a few long delays, many of them caused by component shortages (average 15.3 days late).
- **Limitation:** the average is pulled up by a few extreme cases. The **median late delivery is 4 days**.

## C. Installation performance

### 11. Installations Due: **125**
- **Formula:** non-cancelled orders where `Expected_Installation_Date <= as-of date`.
- **Interpretation:** "scheduled" in this dataset means the order has a promised installation date.
- **Limitation:** there is no field for the date an installation was booked with a technician.

### 12. Completed Installations: **121**
- **Formula:** non-cancelled orders with an installation date, or with status Completed.
- **Interpretation:** 117 of these were among the 125 that were due. The other 4 were installed before their promise date.

### 13. Pending Installations: **14**
- **Formula:** `COUNTIFS(Delivered,1,Installed,0)`.
- **Business meaning:** machines delivered to the customer but not yet working.
- **Interpretation:** 7 of the 14 are already past their installation promise.

### 14. Installation Completion Rate: **93.6%**
- **Formula:** Due & installed ÷ Installations due, which is 117 ÷ 125.
- **Interpretation:** lower than delivery completion (98.5%). Work gets stuck after delivery more often than before it.

### 15. Average Installation Duration: **6.7 days**
- **Business meaning:** the time from delivery to installation, i.e. how long a delivered machine waits.
- **Formula:** `AVERAGE(Actual_Installation_Date − Actual_Delivery_Date)`.
- **Exclusions:**
  - 2 rows installed *before* delivery (an impossible sequence);
  - 1 Completed order with no installation date.
- **Companion measures:**
  - **on-time installation rate 60.2%** (71 of 118);
  - late installations average **10.4 days** late.
- **Interpretation:** installation is the weakest stage of the process.

## D. Efficiency and pending work

### 16. Overdue Orders: **9**
- **Business meaning:** open orders that have already broken a promise.
- **Formula:** a Pending order counts as overdue in either of these cases:
  - it is not yet delivered and the delivery promise date is before the as-of date;
  - it is delivered, not installed, and the installation promise date is before the as-of date.
- **Exclusions:**
  - Completed and Cancelled orders;
  - orders whose promise falls after 30 Jun 2026.
- **Interpretation:** 7 are stuck at installation and 2 at delivery. They are on average **38.6 days** overdue, and the oldest is **81 days**.
- **Limitation:** this depends on the as-of date. Change cell C4 on the KPI ANALYSIS sheet and the result recalculates.

### Supporting time measures
- **Average production time (order → dispatch):** 13.2 days, the largest share of the cycle.
- **Average transit time (dispatch → delivery):** 3.1 days.
- **Average order fulfilment time (order → delivery):** 16.0 days.
- **Average order cycle time (order → installation, completed orders):** 22.4 days.

## E. Order value

### 17. Total Order Value: **₹11.20 crore (simulated)**
- **Formula:** `SUMIFS(Order_Value_INR, Status, "<>Cancelled")`.
- **Applicable records:** 148 of the 151 non-cancelled orders.
- **Exclusions:** 3 orders with a missing value, which were kept blank rather than estimated.
- **Companion measure:** completed order value is ₹8.46 crore.
- **Limitation:** values are illustrative ranges, not real prices or revenue. They are included only to show how a value-weighted backlog is reported.

## F. Data-quality indicators

| Indicator | Result |
|---|---|
| Rows carrying a data-quality flag | 9 of 160 |
| Late deliveries with no recorded reason | 8 of 37 |
| Late installations with no recorded reason | 14 of 47 |
| Orders missing a value | 3 |

## KPIs deliberately **not** calculated

| KPI | Why not |
|---|---|
| Order processing time (order → confirmation) | No order-confirmation date in the data |
| Technician productivity | No technician field |
| Cost of delay / revenue impact | No cost data; synthetic values would make any figure meaningless |
| Customer satisfaction | No survey or complaint data |
