# Interview Preparation Guide

Simple English. Every number here matches the workbook, the dashboard and the reports. Remember: **all data is simulated.**

---

## 0. Be honest about how the project was made (read this first)

This project was built with help from an AI assistant: it generated the data, wrote the code and drafted the documents. Recruiters care about **what you understand and can do**, so:

**Before you put it on your CV, do these yourself (about 3–4 hours in total):**
1. Open the Excel file. Change the as-of date in `KPI ANALYSIS` cell C4 to 15-Jun-2026 and watch the KPIs change. Then change it back.
2. Recalculate 3 KPIs by hand with your own formulas on a new sheet (On-Time Delivery Rate, Overdue Orders, Installation Completion Rate) and check that they match.
3. Build a real **PivotTable + slicer** by following the 5 steps at the bottom of `PIVOT ANALYSIS`. This becomes your own addition.
4. Use the dashboard filters, find NHP-0059 (81 days overdue), and explain why it is overdue.
5. Run the Streamlit dashboard on your laptop (see the README).
6. Read the Data Quality Report and be able to explain any 5 cleaning rules.

**If someone asks "Did you use AI?", answer honestly:**
> "Yes, I used an AI assistant to help generate the synthetic dataset and the code, the way analysts use templates and tools. I defined the business questions, checked every KPI definition, reconciled the numbers myself, and I can explain every formula and decision."

**Never say:**
- that the results are real company results;
- that you worked at the company as an Operations Analyst;
- that your recommendations improved anything.

---

## 1. 30-second introduction

> "I built an Order Fulfilment and Installation Performance dashboard as a case study for a heat-pump manufacturer, Neo Heat Pump. Because I didn't have access to real records, I used a simulated dataset of 160 orders. I cleaned the raw data, defined 17 core KPIs with clear rules, and built an Excel dashboard and a web dashboard. The main finding was that deliveries almost always happen, but only about 72% arrive on time, and installation is the weakest stage at 60% on time. So I recommended a daily overdue-order review and a site-readiness check before installation."

## 2. 60-second explanation

> "A business that makes, delivers and installs heat pumps needs to know what is done, what is still open, and what is late. I started with a raw export of 163 rows. It had duplicate rows, different spellings of statuses, dates in two formats and even an impossible date, 31st February. I cleaned it with written rules and logged all 48 changes, so nothing was changed silently.
>
> Then I calculated KPIs with clear denominators. For example, on-time delivery only counts orders that were actually delivered, so pending and cancelled orders don't distort it. I built an Excel workbook where every number is a formula, with a dashboard you can filter by product, customer type and region, plus a Streamlit web version.
>
> The results: 98.5% of due deliveries were made, but only 72.4% on time. 23 of the 37 late deliveries were commercial or custom orders. Installation was worse, at 60% on time, and half of the late installations happened even though delivery was on time, mostly because the customer's site wasn't ready. There were 9 overdue orders, 7 of them waiting for installation. I recommended a daily overdue review, a site-readiness check, and setting promise dates by product category."

## 3. Two-minute answer (structure: Situation → Task → Action → Result → Learning)

- **Situation:** a heat-pump manufacturer handles orders from booking to installation, and managers lack one reliable view of performance.
- **Task:** turn raw order records into trusted KPIs, a dashboard, and evidence-based recommendations.
- **Action:**
  1. **Data quality first.** Removed 3 duplicate rows, standardised 24 text labels, converted dates, and flagged 9 problem rows instead of deleting them.
  2. **Definitions.** Separated four rates that people often mix up: order completion (80.1%), delivery completion (98.5%), on-time delivery (72.4%) and installation completion (93.6%).
  3. **Overdue logic.** Used a fixed report date (30 June 2026). An order counts as overdue only if its promise for its *current stage* had already passed.
  4. **Tools.** Excel formulas such as COUNTIFS, SUMIFS, AVERAGEIFS and INDEX/MATCH, a filterable dashboard, and a Python/Streamlit web dashboard.
  5. **Reconciliation.** Recalculated every KPI independently and compared: 175 checks, 0 differences.
- **Result:**
  - Delivery problems were concentrated in commercial and custom orders.
  - Installation was the bottleneck: 60.2% on time, 14 machines waiting, 7 overdue.
  - I gave 9 recommendations, prioritised by impact, effort and urgency, each with a metric to track.
- **Learning:** defining the denominator matters more than the chart, and data cleaning took more time than building the dashboard.

## 4. The business problem

Managers can't easily answer these questions:
- How many orders are done, open or cancelled?
- Are we keeping our delivery and installation promises?
- Which open orders are already late?
- Where in the process does work get stuck?

## 5. Why I selected this project

- Operations analyst roles are about order flow, delays, backlogs and KPIs. This project covers all of them.
- Manufacturing plus installation has **two promises** (delivery and installation), which makes the analysis richer than simple e-commerce data.
- Heat pumps are a real, growing industry in India.

## 6. How the data was created

- There were no authorised real records, so I used a **synthetic dataset**: 160 orders from January to June 2026, made reproducible with a fixed random seed.
- I deliberately added realistic errors so I could practise cleaning. The list of these errors is in the repository.
- Some patterns were designed into the data, for example that custom orders take longer to build. **So my findings show my method works, not facts about the company.**

**With real data, I would:**
1. get permission;
2. remove personal details;
3. use the same workbook and checks;
4. compare against this baseline.

## 7. How the data was cleaned (10 rules)

1. Trimmed spaces from IDs.
2. Removed exact duplicate rows.
3. Standardised spellings.
4. Converted text dates; set an impossible date blank and flagged it.
5. Converted values typed as text into numbers; left missing values blank.
6. Kept impossible date sequences but excluded them from timing KPIs.
7. Kept Completed orders that had no installation date, flagged them, and excluded them from installation timing.
8. Did not treat a cancelled order that was delivered and returned as a delivery failure.
9. Never invented missing reasons.
10. Never counted a future promise as overdue.

## 8. The KPIs

- **Order management:** Total 160 · Completed 121 · Pending 30 · Cancelled 9 · Completion rate 80.1% · Backlog 30 orders.
- **Delivery:** Due 132 · Delivery completion 98.5% · On-time 72.4% · Late 37 · Average delay 6.7 days (median 4).
- **Installation:** Due 125 · Completion 93.6% · On-time 60.2% · Pending 14 · Average delivery→installation 6.7 days.
- **Efficiency:** Overdue 9 · Production 13.2 d · Transit 3.1 d · Order cycle 22.4 d · Order value ₹11.20 crore (simulated).

## 9. How the dashboard was built

- **Excel:**
  - KPI cards are formulas;
  - three dropdowns (category, customer type, region) set a helper column `In_Dashboard_Filter` to 1 or 0;
  - every card, chart and the overdue list then count only rows where it is 1;
  - the top-10 overdue list uses LARGE + MATCH + INDEX.
- **Streamlit:**
  - reads the cleaned CSV;
  - applies the same KPI rules from one Python file;
  - has six tabs and sidebar filters.

## 10. Three most important findings

1. **Promises are missed on about 1 in 4 deliveries (72.4% on time).** 23 of the 37 late deliveries are Commercial or Custom orders, which take 15–33 days to build against 5 days for water heaters.
2. **Installation is the bottleneck.** It is 60.2% on time, and 24 of the 47 late installations happened after an on-time delivery, mostly with the reason "customer site not ready".
3. **Overdue work sits at installation.** There are 9 overdue orders, 7 waiting for installation, on average 38.6 days late; the oldest is 81 days.

## 11. Recommendations (top 3)

1. A daily 10-minute review of overdue and delivered-not-installed orders.
2. A readiness call 3–5 days before delivery; book the installation only when the site is ready.
3. Promise dates per product category, based on actual production time.

Each recommendation comes with a metric to track. None has been implemented, so I don't claim results.

## 12. Tools used and why

- **Excel:** the standard tool in operations and MIS teams.
- **Python (pandas):** repeatable cleaning and an audit trail.
- **Streamlit:** a quick, shareable web dashboard.
- **GitHub:** a portfolio that people can browse.

## 13. Challenges

- **Rates that sound the same.** Order completion and delivery completion sound alike but are different, so I wrote four separate definitions.
- **What "overdue" means.** At first, all pending orders looked late. A fixed report date and stage-based promises fixed this.
- **Dirty dates.** One date was impossible (31-02-2026), and two installations were dated before delivery. I had to decide between excluding and correcting, and I chose to exclude.
- **Tool limits.** The spreadsheet generator couldn't create PivotTables, so I used formula tables and documented how to add one.

## 14. Limitations

- The data is simulated, so the findings can't describe the real company.
- Groups are small (for example, only 21 timed deliveries to Other States).
- Reasons are self-reported and sometimes missing.
- There is no technician, cost or customer-satisfaction data.

## 15. What I would improve next

- Use authorised real data.
- Add an installation booking date and technician ID.
- Add a Power BI version.
- Track weekly trends.
- Use the median as well as the mean.
- Add a simple forecast of the backlog.

## 16. Likely interview questions and simple answers

1. **What is the difference between order completion rate and on-time delivery rate?**
   Order completion = completed ÷ non-cancelled orders (80.1%). On-time delivery = delivered on or before the promise ÷ orders actually delivered with valid dates (72.4%). One measures *done*, the other measures *on time*.
2. **Why did you exclude cancelled orders from delivery KPIs?**
   A cancelled order is not a failed delivery. Counting it would make delivery performance look worse for the wrong reason.
3. **Why not count pending orders as late?**
   Many have promises after the report date, so they aren't due yet. Only pending orders past their promise are overdue: 9 of the 30.
4. **What is a denominator and why does it matter?**
   It is the "out of how many" part of a rate. If you pick the wrong one, the percentage is meaningless.
5. **How did you handle missing data?**
   I left it blank, flagged it, and excluded it only from the metric it affects. I never guessed.
6. **What would you do with the 31-February date?**
   Set it blank, flag the row, exclude it from delivery timing, and ask the data owner for the correct date.
7. **What does COUNTIFS do?**
   It counts rows that meet several conditions. For example, count orders where the category is Custom *and* the status is Pending.
8. **How does your dashboard filter work?**
   A helper column is 1 when a row matches the dropdown choices. All formulas count only the rows marked 1.
9. **Which KPI would you show the CEO first?**
   Overdue orders and on-time delivery. They show promises that have already been broken.
10. **What is the biggest bottleneck?**
    In time, production (13.2 days on average). In reliability, installation (60.2% on time).
11. **How do you know your numbers are right?**
    I recalculated every KPI separately and compared it with the Excel results: 175 checks, 0 differences. The status counts also add up (121 + 30 + 9 = 160).
12. **What is the average order cycle time?**
    22.4 days from order to installation, for completed orders.
13. **Why use the median as well as the average?**
    A few very late orders (up to 60 days) pull the average up to 6.7 days. The median late delivery is 4 days.
14. **Is "customer site not ready" really the cause?**
    It's the most common *recorded* reason, so I call it a hypothesis. To confirm it, I'd need the site-readiness date and the number of reschedules.
15. **What data would you ask for in a real company?**
    Order confirmation date, installation booking date, technician, re-promised dates, cost of delays, and complaints.
16. **How would you measure whether your recommendation worked?**
    Freeze today's numbers as a baseline, pilot the change, and compare the same KPI over 8+ weeks.
17. **Why Excel and not only Python?**
    Most operations teams use Excel daily, and managers can open it without installing anything.
18. **What is a backlog?**
    Open orders not yet finished: here 30 orders, ₹2.74 crore (simulated).
19. **What is the difference between "due" and "overdue"?**
    Due means the promise date has arrived. Overdue means it has passed and the work still isn't done.
20. **Why is June's completion rate low?**
    Most June orders were not yet due on 30 June. That is a timing effect, not a performance problem.
21. **Why did you use synthetic data?**
    I didn't have authorised real data, and real customer data must not be published. Synthetic data let me show the method safely, and I label it clearly everywhere.
22. **What would you automate next?**
    A weekly refresh: drop in the new export, run the cleaning, and the workbook and dashboard update.
23. **What is an Operations Analyst's job, in one line?**
    Turn operational data into clear numbers that help managers fix delays and use resources better.

## 17. Plain-language glossary

- **KPI:** a key number that shows performance.
- **Backlog:** open work.
- **Lead time:** how long something takes.
- **Bottleneck:** the slowest point, where work piles up.
- **As-of date:** the date the report is "taken".
- **Reconciliation:** checking that numbers agree from two directions.
- **Synthetic data:** realistic but made-up data.
