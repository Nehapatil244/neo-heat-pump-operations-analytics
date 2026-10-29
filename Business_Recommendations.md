# Business Recommendations

> All recommendations are **proposals** based on **simulated data**. None has been implemented, and no improvement is claimed. Any targets mentioned are suggestions to agree with management, not forecasts.

Priority is based on **impact** (how much of the observed problem it addresses), **effort** (cost and complexity) and **urgency** (how quickly the problem grows if ignored).

## Priority 1: do now (high impact, low effort)

### R1. Daily overdue and awaiting-installation review
- **Observed result:** 9 overdue orders, 7 stuck at installation, on average 38.6 days overdue (oldest 81 days). A further 14 delivered machines are awaiting installation.
- **Possible explanation (hypothesis):** nobody owns an order once it has been delivered.
- **Recommendation:** hold a 10-minute daily stand-up using the dashboard's *Pending & overdue* tab. For each order, record the owner, the next step, the revised date and whether the customer has been informed.
- **Expected benefit (not verified):** fewer forgotten orders and earlier customer communication.
- **Metrics to monitor:** Overdue Orders, Average Days Overdue, Pending Installations.
- **Owner:** operations coordinator.

### R2. Pre-installation site-readiness check
- **Observed result:**
  - on-time installation is 60.2%;
  - 24 of 47 late installations followed an on-time delivery;
  - 15 of those 24 cite "Customer site not ready".
- **Possible explanation (hypothesis):** installation slots are booked before the customer's civil, electrical or plumbing work is finished.
- **Recommendation:** make a readiness call or send a checklist 3–5 days before delivery, and confirm the installation slot only once the site is ready.
- **Expected benefit (not verified):** fewer installations delayed by the customer's site.
- **Metrics to monitor:** On-Time Installation Rate, and the number of late installations with the reason "Customer site not ready".
- **Owner:** installation supervisor with customer service.

### R5. Mandatory delay-reason dropdown
- **Observed result:** no reason on 8 of 37 late deliveries and 14 of 47 late installations.
- **Recommendation:** whenever a promised date passes, require a reason chosen from a fixed list.
- **Expected benefit (not verified):** root causes become measurable.
- **Metric to monitor:** percentage of late records with a reason (suggested target to discuss: 100%).
- **Owner:** operations analyst or data owner.

### R8. Weekly operations KPI report
- **Recommendation:** each week, publish on-time delivery and installation (overall and by category), overdue count and age, pending installations, and reason completeness. Use the workbook or the dashboard.
- **Expected benefit (not verified):** problems are seen weekly rather than at month end.
- **Metric to monitor:** the report is issued every week and its actions are closed.
- **Owner:** operations analyst.

## Priority 2: plan within 1–2 months (high or medium impact, medium effort)

### R3. Promise dates set by product category
- **Observed result:**
  - on-time delivery is 42.9% for Custom and 55.9% for Commercial, against 90.0% for water heaters;
  - average production takes 32.9 days for Custom and 15.5 days for Commercial, against 5.0 days for water heaters.
- **Recommendation:** set each category's promised lead time from actual production history (for example, the median plus a buffer) and review it quarterly.
- **Expected benefit (not verified):** promises that match capacity, giving higher on-time delivery where it is weakest.
- **Metrics to monitor:** on-time delivery by category, and the gap between promised and actual lead time.
- **Owner:** sales operations with production planning.

### R4. Component check at order acceptance
- **Observed result:** "Component shortage" late deliveries average 15.3 days late, the longest of any reason.
- **Recommendation:** for Custom and Commercial orders, confirm critical component availability before committing to a date.
- **Metrics to monitor:** late deliveries with the reason "Component shortage", and the maximum delivery delay.
- **Owner:** procurement and stores.

### R6. One order tracker with validated fields
- **Observed result:** the raw export needed 48 corrections or flags, including 3 duplicate rows and an impossible date.
- **Recommendation:** use a single shared tracker with:
  - dropdown statuses;
  - real date fields with sequence validation;
  - a unique Order ID;
  - a dispatch date;
  - an installation booking date.
- **Metric to monitor:** rows with data-quality flags per month (target: 0).
- **Owner:** operations analyst.

### R7. Installation scheduling and capacity
- **Observed result:** only 4 late installations cite "Technician availability" (2 of them from May orders). That is too few to confirm a peak-season effect, so this is a precaution, not a proven fix.
- **Recommendation:** keep a shared technician calendar and plan capacity before peak months.
- **Metrics to monitor:** delivery→installation days, and late installations caused by technician availability.
- **Owner:** installation supervisor.

## Priority 3: review

### R9. Transit allowance for Other States
- **Observed result:** Other States are on time 52.4% of the time (21 timed deliveries), against 78.5% for Bengaluru.
- **Recommendation:** review the transit buffer and agree pickup dates with transporters at dispatch.
- **Metrics to monitor:** on-time delivery for Other States, and average transit days.
- **Owner:** dispatch and logistics.

## How improvement should be evaluated

1. Freeze the current numbers (this report) as the **baseline**.
2. Introduce changes one at a time, ideally first on a pilot group (for example, R2 on Bengaluru installations only).
3. Compare at least 8 weeks of results against the baseline using the same KPI definitions.
4. Report an improvement only when it is measured on real, authorised data.
