"""Step 9 - Build reports/Case_Study.pdf (HTML -> PDF with Playwright). Numbers come from analysis/results.json."""
import json, pathlib, base64
from playwright.sync_api import sync_playwright
ROOT = pathlib.Path(__file__).resolve().parents[1]
R = json.load(open(ROOT / "analysis/results.json")); K = R["kpis"]
cat = {r["Product_Category"]: r for r in R["Product_Category"]}
reg = {r["Region"]: r for r in R["Region"]}
def img(name):
    return "data:image/png;base64," + base64.b64encode((ROOT / "screenshots" / name).read_bytes()).decode()
p = lambda x: f"{x*100:.1f}%"
late_i_total = R["late_install_knock_on"] + R["late_install_with_ontime_delivery"] + R["late_install_delivery_unknown"]

html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@page {{ size: A4; margin: 16mm 15mm 16mm 15mm; }}
body {{ font-family: Arial, Helvetica, sans-serif; color:#2D3136; font-size:10.5pt; line-height:1.45; }}
h1 {{ font-size:24pt; margin:0 0 4px; }} h2 {{ font-size:14.5pt; color:#0f8a88; border-bottom:2px solid #16B8B5; padding-bottom:3px; margin:18px 0 8px; }}
h3 {{ font-size:11.5pt; margin:12px 0 4px; }}
.cover {{ background:#2D3136; color:white; padding:30px 28px; border-radius:8px; }}
.cover p {{ color:#cfd5da; margin:6px 0 0; }}
.warn {{ background:#FDECEA; color:#b23b37; border-left:5px solid #D9534F; padding:9px 12px; border-radius:4px; font-weight:bold; margin:14px 0; font-size:9.5pt; }}
.kpis {{ display:grid; grid-template-columns: repeat(4, 1fr); gap:8px; margin:10px 0; }}
.k {{ background:#F4F6F8; border-top:4px solid #16B8B5; border-radius:6px; padding:8px 10px; }}
.k b {{ display:block; font-size:17pt; }} .k span {{ font-size:8pt; color:#6b747c; text-transform:uppercase; font-weight:bold; }}
.k.r {{ border-top-color:#D9534F; }} .k.r b {{ color:#D9534F; }}
table {{ border-collapse:collapse; width:100%; font-size:9pt; margin:6px 0 10px; }}
th {{ background:#2D3136; color:white; text-align:left; padding:5px 6px; }} td {{ border-bottom:1px solid #e1e5e8; padding:5px 6px; vertical-align:top; }}
img {{ width:100%; border:1px solid #dde2e6; border-radius:4px; margin:6px 0; }}
.pb {{ }} img, tr, .find, .k {{ page-break-inside: avoid; }} h2 {{ page-break-after: avoid; }} .muted {{ color:#6b747c; font-size:9pt; }}
.find {{ border-left:4px solid #16B8B5; background:#fafbfc; padding:6px 10px; margin:6px 0; }}
</style></head><body>
<div class="cover"><h1>Order Fulfilment &amp; Installation Performance Analysis Dashboard</h1>
<p>Business Operations Analytics Case Study · Neo Heat Pump – Sai Heating and Cooling Solutions</p>
<p>Orders Jan–Jun 2026 · Report as of 30 Jun 2026 · Prepared by [Your Name]</p></div>
<div class="warn">SIMULATED DATA: all 160 orders are synthetic records created for a portfolio case study. Results do not describe the real performance of the company. Recommendations are proposals, not implemented actions.</div>
<div class="kpis">
<div class="k"><span>Total orders</span><b>{K['total_orders']}</b>{K['completed']} completed · {K['pending']} pending · {K['cancelled']} cancelled</div>
<div class="k"><span>On-time delivery</span><b>{p(K['on_time_delivery_rate'])}</b>{K['late_deliveries']} late of {K['deliveries_timed']}</div>
<div class="k"><span>On-time installation</span><b>{p(K['on_time_install_rate'])}</b>{K['late_installs']} late of {K['installs_timed']}</div>
<div class="k r"><span>Overdue orders</span><b>{K['overdue_orders']}</b>{K['overdue_install_stage']} stuck at installation</div></div>

<h2>1. Business background</h2>
<p>Neo Heat Pump (Sai Heating and Cooling Solutions) supplies heat pumps, heat-pump water heaters, swimming-pool heat pumps, heat-pump dryers and customer-specific solutions. Each order is manufactured, dispatched, delivered and then installed on the customer's site. That means two promises are made to the customer: a <b>delivery date</b> and an <b>installation date</b>. No company history, revenue or real performance figures are used in this case study.</p>
<h2>2. Problem statement</h2>
<p>Management has no single, trusted view of: how much work is completed, pending or cancelled; whether delivery and installation promises are kept; which open orders are already late; and which stage of the process causes the most delay.</p>
<h2>3. Analytical objectives</h2>
<ol><li>Clean and validate the raw order export, with every change logged.</li><li>Define KPIs with explicit numerators, denominators and exclusions.</li>
<li>Build a filterable Excel dashboard and a web dashboard from the same rules.</li><li>Identify bottlenecks and recommend prioritised, measurable actions.</li></ol>

<h2>4. Data and methodology</h2>
<table><tr><th>Step</th><th>Detail</th></tr>
<tr><td>Data</td><td>163-row synthetic raw export → 160 unique orders; 5 product families, 3 customer types, 3 regions; anonymous customer codes; illustrative order values</td></tr>
<tr><td>Cleaning</td><td>3 duplicate rows removed; 24 inconsistent labels standardised; 6 alternate-format dates converted; 1 impossible date (31-02-2026) blanked and flagged; 3 impossible date sequences kept but excluded from timing; 48-entry cleaning log</td></tr>
<tr><td>Derived fields</td><td>Delivery/installation delay days, production/transit/installation durations, current stage, overdue flag and days overdue (judged at a fixed as-of date)</td></tr>
<tr><td>Tools</td><td>Excel (COUNTIFS, SUMIFS, AVERAGEIFS, INDEX/MATCH, LARGE, data validation, charts) · Python/pandas · Streamlit/Plotly</td></tr>
<tr><td>QA</td><td>Every workbook KPI recalculated independently in Python: 175 checks, 0 differences; status counts reconcile (121 + 30 + 9 = 160)</td></tr></table>

<h2>5. KPI calculations</h2>
<table><tr><th>KPI</th><th>Definition (numerator ÷ denominator)</th><th>Result</th></tr>
<tr><td>Order completion rate</td><td>Completed ÷ non-cancelled orders ({K['completed']} ÷ {K['active_orders']})</td><td><b>{p(K['order_completion_rate'])}</b></td></tr>
<tr><td>Cancellation rate</td><td>Cancelled ÷ total orders</td><td>{p(K['cancellation_rate'])}</td></tr>
<tr><td>Current backlog</td><td>Pending orders (value, simulated)</td><td>{K['backlog']} (₹{K['backlog_value']/1e7:.2f} Cr)</td></tr>
<tr><td>Delivery completion rate</td><td>Due &amp; delivered ÷ deliveries due ({K['deliveries_due_done']} ÷ {K['deliveries_due']})</td><td>{p(K['delivery_completion_rate'])}</td></tr>
<tr><td>On-time delivery rate</td><td>Delivered on/before promise ÷ delivered with valid dates ({K['on_time_deliveries']} ÷ {K['deliveries_timed']})</td><td><b>{p(K['on_time_delivery_rate'])}</b></td></tr>
<tr><td>Average delivery delay</td><td>Mean days late, late deliveries only (max {K['max_delivery_delay']:.0f})</td><td>{K['avg_delivery_delay_late']:.1f} d</td></tr>
<tr><td>Installation completion rate</td><td>Due &amp; installed ÷ installations due ({K['installs_due_done']} ÷ {K['installs_due']})</td><td>{p(K['installation_completion_rate'])}</td></tr>
<tr><td>On-time installation rate</td><td>Installed on/before promise ÷ installed with valid dates</td><td><b>{p(K['on_time_install_rate'])}</b></td></tr>
<tr><td>Pending installations</td><td>Delivered, not installed</td><td>{K['pending_installations']}</td></tr>
<tr><td>Average installation duration</td><td>Delivery → installation</td><td>{K['avg_install_duration']:.1f} d</td></tr>
<tr><td>Overdue orders</td><td>Pending and past the promise for the current stage</td><td><b>{K['overdue_orders']}</b> (avg {K['avg_days_overdue']:.1f} d)</td></tr>
<tr><td>Order cycle time</td><td>Order → installation, completed orders</td><td>{K['avg_order_cycle']:.1f} d</td></tr>
<tr><td>Total order value</td><td>Non-cancelled, simulated</td><td>₹{K['total_order_value']/1e7:.2f} Cr</td></tr></table>
<p class="muted">Cancelled orders are excluded from delivery and installation KPIs. Promises after the as-of date are "not yet due", never overdue.</p>

<h2>6. Dashboard design</h2>
<p>The Excel dashboard has 8 KPI cards, 6 charts and a "most overdue" action list. Three dropdown filters (category, customer type, region) drive every element through a helper column, so all values remain live formulas.</p>
<img src="{img('excel_dashboard.png')}">

<h2>Web dashboard (Streamlit)</h2>
<p>The web dashboard has six tabs (Overview, Delivery, Installation, Pending &amp; overdue, Findings, Data &amp; method) with filters for date, category, status, customer type and region. It reads the cleaned dataset and applies the same KPI rules.</p>
<img src="{img('dashboard_preview.png')}">
<img src="{img('dashboard_installation.png')}" style="max-height:330px; object-fit:cover; object-position:top;">

<h2>7. Key findings</h2>
<div class="find"><b>F1 · About 1 in 4 deliveries misses the promise.</b> On-time delivery is {p(K['on_time_delivery_rate'])}, yet {p(K['delivery_completion_rate'])} of due deliveries were made. The problem is lateness, not missed deliveries.</div>
<div class="find"><b>F2 · Delays concentrate in Commercial and Custom orders.</b> On-time delivery is {p(cat['Custom Requirement']['On-time delivery %'])} for Custom and {p(cat['Commercial Heat Pump']['On-time delivery %'])} for Commercial, against {p(cat['Heat Pump Water Heater']['On-time delivery %'])} for water heaters. Together these two categories account for {R['big_vs_rest']['big_late']} of {K['late_deliveries']} late deliveries. Average production is {cat['Custom Requirement']['Avg production (d)']:.1f} d for Custom against {cat['Heat Pump Water Heater']['Avg production (d)']:.1f} d for water heaters.</div>
<div class="find"><b>F3 · Installation is the weakest stage.</b> On-time installation is {p(K['on_time_install_rate'])} against {p(K['on_time_delivery_rate'])} for delivery, and installation completion is {p(K['installation_completion_rate'])} against {p(K['delivery_completion_rate'])}.</div>
<div class="find"><b>F4 · Half of the late installations followed an on-time delivery.</b> {R['late_install_with_ontime_delivery']} of {late_i_total} did. The most frequent recorded reason was "Customer site not ready" ({R['install_reasons'].get('Customer site not ready', 0)} late installations).</div>
<div class="find"><b>F5 · Overdue work sits at installation.</b> {K['overdue_orders']} orders are overdue: {K['overdue_install_stage']} at installation and {K['overdue_delivery_stage']} at delivery. They are {K['avg_days_overdue']:.1f} days overdue on average, and the oldest is {K['max_days_overdue']:.0f} days.</div>
<div class="find"><b>F6 · Production is the largest share of cycle time.</b> Production takes {K['avg_production']:.1f} d, transit {K['avg_transit']:.1f} d and delivery→installation {K['avg_install_duration']:.1f} d, against an average cycle of {K['avg_order_cycle']:.1f} d.</div>
<div class="find"><b>F7 · Other States are on time less often</b> ({p(reg['Other States']['On-time delivery %'])} against {p(reg['Bengaluru']['On-time delivery %'])} for Bengaluru). This is a small sample of {reg['Other States']['Timed deliveries']} timed deliveries.</div>
<div class="find"><b>F8 · Reasons are missing</b> on {K['late_del_noreason']} of {K['late_deliveries']} late deliveries and {K['late_inst_noreason']} of {K['late_installs']} late installations.</div>
<p class="muted">Causes are hypotheses supported only by recorded reason codes. Several patterns were assumptions built into the simulation.</p>

<h2>8. Business recommendations</h2>
<table><tr><th>#</th><th>Recommendation</th><th>Impact / Effort / Urgency</th><th>Metric to monitor</th></tr>
<tr><td>R1</td><td>Daily review of overdue and delivered-not-installed orders</td><td>High / Low / Immediate</td><td>Overdue orders, days overdue</td></tr>
<tr><td>R2</td><td>Site-readiness check 3–5 days before delivery; book the installation slot only once the site is ready</td><td>High / Low / 2 weeks</td><td>On-time installation rate</td></tr>
<tr><td>R3</td><td>Promise dates by product category, based on actual production time</td><td>High / Medium / 1 month</td><td>On-time delivery by category</td></tr>
<tr><td>R4</td><td>Component check at order acceptance (Custom and Commercial)</td><td>Medium / Medium</td><td>Component-shortage delays</td></tr>
<tr><td>R5</td><td>Mandatory delay-reason dropdown</td><td>Medium / Low</td><td>% of late records with a reason</td></tr>
<tr><td>R6</td><td>One tracker with validated statuses and dates</td><td>Medium / Low</td><td>Data-quality flags per month</td></tr>
<tr><td>R7</td><td>Technician calendar and capacity plan</td><td>Medium / Medium</td><td>Delivery→installation days</td></tr>
<tr><td>R8</td><td>Weekly KPI report</td><td>Medium / Low</td><td>Report issued weekly</td></tr>
<tr><td>R9</td><td>Review transit allowance for Other States</td><td>Low / Low</td><td>On-time delivery, Other States</td></tr></table>

<h2>9. Limitations</h2>
<ul><li>The data is simulated, so the results do not describe the company. Some patterns were designed into the generator.</li>
<li>Groups are small: each product category has 14–40 timed deliveries, and Other States has only 21.</li>
<li>Reason codes are self-reported and sometimes missing. Causes are hypotheses.</li>
<li>There is no installation booking date, technician, cost or customer-satisfaction data.</li>
<li>Overdue status depends on the chosen as-of date (30 Jun 2026).</li></ul>

<h2>10. What I learned</h2>
<ul><li>Choosing the right <b>denominator</b> matters more than the chart. Completion, delivery completion, on-time delivery and installation completion are four different questions.</li>
<li>Data cleaning is most of the work. Logging every change makes the numbers defensible.</li>
<li>"Not yet due" is not "late". A fixed report date keeps the overdue logic honest.</li>
<li>A finding is not a cause. Separating observations from hypotheses, and naming the data needed to confirm them, is part of the analyst's job.</li>
<li>Reconciling results from two independent calculations catches mistakes before a manager does.</li></ul>
<p class="muted">Repository: [GitHub URL] · Excel workbook: excel/operations_analysis.xlsx · Dashboard: dashboard/app.py</p>
</body></html>"""
tmp = ROOT / "reports/_case_study.html"
tmp.write_text(html, encoding="utf-8")
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page()
    pg.goto(tmp.as_uri()); pg.wait_for_timeout(500)
    pg.pdf(path=str(ROOT / "reports/Case_Study.pdf"), format="A4", print_background=True,
           margin={"top": "14mm", "bottom": "14mm", "left": "13mm", "right": "13mm"})
    b.close()
tmp.unlink()
print("wrote reports/Case_Study.pdf")
