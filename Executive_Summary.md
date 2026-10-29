# Executive Summary & Business Analysis

**Order Fulfilment & Installation Performance Analysis**: a case study for Neo Heat Pump (Sai Heating and Cooling Solutions)
Period: orders booked 1 Jan – 30 Jun 2026 · Report as-of date: 30 Jun 2026 · Prepared by: [Your Name]

> **Simulated data.** All 160 orders are synthetic records created for a portfolio case study. Some patterns, such as custom orders taking longer to build, were **assumptions built into the simulation**. The findings therefore demonstrate an analysis method; they do not reveal real company performance or real causes. Recommendations are proposals and have not been implemented.

---

## 1. Executive summary

**Business problem.** A heat-pump business that manufactures, delivers and installs equipment needs one reliable answer to four questions:
- How much work is done, open or cancelled?
- Are delivery and installation promises being kept?
- Which open orders are already late?
- Where in the process does work get stuck?

**Approach.**
1. Cleaned a 163-row raw order export: removed 3 duplicate rows, recorded 48 changes or flags, and broke no business data silently.
2. Derived stage durations and overdue flags.
3. Calculated 42 KPIs with explicit numerators, denominators and exclusions.
4. Built an Excel workbook (live formulas, filterable dashboard) and a Streamlit web dashboard.
5. Reconciled both against an independent Python calculation: 175 checks, 0 differences.

**Most important results (simulated data):**

| Area | Result |
|---|---|
| Orders | 160 booked: 121 completed, 30 pending, 9 cancelled; **order completion rate 80.1%** |
| Delivery | Due deliveries made: **98.5%**; but **on-time delivery only 72.4%** (37 late of 134) |
| Installation | **On-time installation 60.2%**, installation completion 93.6%; **14** delivered machines awaiting installation |
| Overdue | **9 open orders past their promise**: 7 stuck at installation, average 38.6 days overdue |
| Cycle time | 22.4 days order → installation, of which production is 13.2 days |

**Headline:** the factory almost always delivers, but promises are missed in two specific places:
- **Commercial and Custom orders at the delivery stage:** 23 of the 37 late deliveries.
- **The installation stage:** half of the late installations followed an on-time delivery, mostly because the customer's site was not ready.

The three highest-priority recommendations are:
1. A daily review of overdue and awaiting-installation orders.
2. A site-readiness check before installation is booked.
3. Promise dates set by product category.

## 2. Operational performance

### Orders
- 160 orders were booked, rising from 13 in January to 40 in May.
- **Status:** 121 completed (75.6%), 30 pending, 9 cancelled (5.6%).
- **Completion rate:** 80.1% of non-cancelled orders are closed. June is low (32%) because most June promises fall after 30 Jun, which is a timing effect rather than a delay.
- **Backlog:** 30 orders worth ₹2.74 crore (simulated). They sit in production (14), in transit (2) and awaiting installation (14).

### Delivery
- **Completion:** 132 deliveries were due by 30 Jun and 130 were made (98.5%).
- **Timeliness:** 97 of 134 timed deliveries were on time or early (**72.4%**). 37 were late, by 6.7 days on average (median 4, maximum 60).
- **Bias:** across all deliveries the average variance is −1.5 days, meaning most arrive early. The problem is concentrated, not universal.

### Installation
- **Completion:** 125 installations were due and 117 were done (93.6%).
- **Timeliness:** 71 of 118 timed installations were on time (**60.2%**). Late installations averaged 10.4 days late.
- **Waiting time:** a delivered machine waits 6.7 days on average before it is installed. 14 machines are currently waiting, 7 of them past their promise.

## 3. Key findings

| # | Observation | Supporting calculation | Business implication | Recommended action |
|---|---|---|---|---|
| F1 | About 1 in 4 deliveries misses its promised date | 37 late ÷ 134 timed = 27.6% late; on-time 72.4% | Follow-up calls and lost trust (not measured here) | R3 promise dates by category |
| F2 | Late deliveries concentrate in Commercial Heat Pumps and Custom Requirements | On time: Custom 42.9%, Commercial 55.9% vs Water Heater 90.0%. These two = 23 of 37 late. Production: Custom 32.9 d, Commercial 15.5 d vs Water Heater 5.0 d | A single standard lead time does not fit long, variable builds | R3, R4 |
| F3 | Installation is the weakest stage | On-time installation 60.2% vs on-time delivery 72.4%; installation completion 93.6% vs delivery completion 98.5% | A delivered but uninstalled machine does not yet serve the customer | R2 |
| F4 | Half of the late installations followed an **on-time** delivery | 24 of 47 late installations had on-time deliveries. Of those 24, 15 were recorded as "Customer site not ready" and 7 had no reason | Fixing the factory alone will not fix installation lateness | R2, R7 |
| F5 | Overdue work sits mainly at installation and is old | 9 overdue: 7 at installation, 2 at delivery; average 38.6 days, oldest 81 days | Stale open orders tie up value and risk cancellation | R1 |
| F6 | Production is the largest share of cycle time | Production 13.2 d + transit 3.1 d + delivery→installation 6.7 d ≈ 22.4 d cycle | Capacity and material planning are the biggest levers | R3, R4 |
| F7 | Other States are delivered on time less often (small sample) | Other States 52.4% (21 timed) vs Bengaluru 78.5% (79 timed) | Transit allowances may be too tight | R9 |
| F8 | Reason data is incomplete | No reason on 8 of 37 late deliveries and 14 of 47 late installations | Root-cause work becomes guesswork | R5 |
| F9 | The raw export was not analysis-ready | 3 duplicate rows, 12 status variants, 7 date-format problems (6 in a second format plus 1 impossible date), 3 impossible date sequences | Unchecked reports would have overstated orders and mis-timed deliveries | R6 |

## 4. Root-cause investigation

The data supports **association**, not proof of cause. Each hypothesis below is labelled with how much the data can support it.

| Problem | What the data shows | Hypothesis | Evidence level | Data needed to confirm |
|---|---|---|---|---|
| Late Commercial/Custom deliveries | Production takes about 3–6× longer than for water heaters and varies more (Custom standard deviation 16.6 d). The "Component shortage" reason averages 15.3 days late | Promise dates ignore real production time; components are not checked when the order is accepted | Moderate (durations calculated; reasons are self-reported) | Bill-of-materials availability date, production start and finish dates, planned versus actual lead time by model |
| Late installations after on-time delivery | 15 of 24 carry the reason "Customer site not ready" | Site readiness (civil, electrical, plumbing work) is not confirmed before the slot is booked | Weak to moderate (reason codes only; 7 have no reason) | Site-survey date, readiness confirmation date, installation booking date, number of reschedules |
| Late installations after late delivery | 23 of 47 late installations followed a late delivery | Knock-on effect: when delivery slips, the installation promise is not re-planned | Moderate | A re-promised installation date field |
| Technician capacity | Only 4 late installations cite "Technician availability" | Possible capacity constraint in busy months (2 of the 4 come from May orders) | Weak (too few cases to conclude) | Technician calendar, jobs per technician per day |
| Other States delays | 10 late out of 21 timed deliveries | Longer and less predictable transport | Weak (small sample) | Transporter pickup and delivery records, distance |

## 5. Recommendations (prioritised)

Full detail is in [Business_Recommendations.md](Business_Recommendations.md). Priority is set by impact, effort and urgency.

| # | Recommendation | Impact | Effort | Urgency |
|---|---|---|---|---|
| R1 | Daily review of overdue and delivered-not-installed orders | High | Low | Immediate |
| R2 | Pre-installation site-readiness check; book the slot only after readiness is confirmed | High | Low | 2 weeks |
| R3 | Promise dates by product category, based on actual production time | High | Medium | 1 month |
| R4 | Component availability check at order acceptance (Custom/Commercial) | Medium | Medium | 1–2 months |
| R5 | Mandatory delay-reason dropdown | Medium | Low | 2 weeks |
| R6 | One order tracker with standard statuses and validated dates | Medium | Low | 1 month |
| R7 | Shared technician calendar and peak-season capacity plan | Medium | Medium | Before next peak |
| R8 | Weekly operations KPI report | Medium | Low | Start now |
| R9 | Review transit allowance for Other States | Low | Low | 1–2 months |

## 6. Limitations

- **Simulated data.** The results do not describe Neo Heat Pump's real performance. The generator assumed some tendencies (longer custom builds, slower transport outside Karnataka, site-readiness delays, peak-season technician pressure), so finding them again shows the method works, not that the business behaves this way.
- **Small groups.** Each product category has 14–40 timed deliveries and Other States has only 21, so small percentage differences are not reliable.
- **Self-reported reasons.** Reason codes are typed by staff, and some are missing.
- **Missing fields.** There is no order-confirmation date, installation booking date, technician, cost, service or complaint data.
- **Single as-of date.** "Overdue" depends on the 30-Jun-2026 report date, and it can be changed in the workbook.
- **One time slice.** Six months is too short to see seasonality with confidence.

## 7. Next steps

1. **Collect better data:**
   - order-confirmation date;
   - installation booking and site-readiness dates;
   - technician ID;
   - re-promised dates;
   - mandatory reason codes;
   - cancellation date.
2. **Monitor weekly:**
   - on-time delivery and installation, by category;
   - overdue count and age;
   - pending installations;
   - reason completeness.
3. **Repeat the analysis on authorised real data** with the same workbook. Paste the anonymised records into CLEANED DATA, update the as-of date, and check that the DATA QUALITY LOG reads OK.
4. **Trial R2 and R3 on a small group of orders** and compare against the baseline. Only then would any improvement be claimed.
