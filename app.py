"""
Order Fulfilment & Installation Performance Dashboard (Streamlit)
Case study: Neo Heat Pump - Sai Heating and Cooling Solutions
DATA IS SIMULATED for a portfolio project. It is not real company performance.

Run locally:
    pip install -r dashboard/requirements.txt
    streamlit run dashboard/app.py
"""
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from kpi_engine import load, compute_kpis, by_group, AS_OF

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "cleaned_orders.csv"
TEAL, CHAR, SILVER, GREEN, AMBER, RED, GREY = "#16B8B5", "#2D3136", "#F4F6F8", "#3AAE4B", "#E8A33D", "#D9534F", "#8A939C"
STATUS_COLORS = {"Completed": TEAL, "Pending": AMBER, "Cancelled": GREY}

st.set_page_config(page_title="Order Fulfilment & Installation Dashboard", page_icon="📦", layout="wide")
st.markdown(f"""
<style>
  .block-container {{padding-top: 1.6rem; max-width: 1350px;}}
  .hero {{background:{CHAR}; color:white; padding:18px 24px; border-radius:10px; margin-bottom:8px;}}
  .hero h1 {{font-size:1.65rem; margin:0; color:white;}}
  .hero p {{margin:4px 0 0 0; color:#cfd5da; font-size:.95rem;}}
  .synthetic {{background:#FDECEA; color:{RED}; border-left:5px solid {RED}; padding:8px 14px; border-radius:6px;
               font-size:.88rem; font-weight:600; margin-bottom:14px;}}
  .card {{background:{SILVER}; border-top:4px solid {TEAL}; border-radius:8px; padding:12px 14px; height:118px;}}
  .card .lab {{font-size:.72rem; letter-spacing:.04em; color:{GREY}; font-weight:700; text-transform:uppercase;}}
  .card .val {{font-size:1.75rem; font-weight:800; color:{CHAR}; line-height:1.25;}}
  .card .sub {{font-size:.76rem; color:{GREY};}}
  .card.red {{border-top-color:{RED};}} .card.red .val {{color:{RED};}}
  .finding {{background:white; border:1px solid #e3e7ea; border-left:5px solid {TEAL}; border-radius:8px; padding:12px 16px; margin-bottom:10px;}}
  .finding b.t {{color:{CHAR}; font-size:1rem;}}
  .tag {{display:inline-block; font-size:.7rem; font-weight:700; padding:2px 8px; border-radius:10px; background:#e8f7f7; color:#0f8a88; margin-left:6px;}}
</style>""", unsafe_allow_html=True)


@st.cache_data
def get_data():
    return load(DATA)


df_all = get_data()
K_ALL = compute_kpis(df_all)

# ------------------------------------------------------------------ sidebar filters
st.sidebar.header("Filters")
dmin, dmax = df_all.Order_Date.min().date(), df_all.Order_Date.max().date()
dr = st.sidebar.date_input("Order date range", (dmin, dmax), min_value=dmin, max_value=dmax)
cats = st.sidebar.multiselect("Product category", sorted(df_all.Product_Category.unique()), placeholder="All categories")
stats = st.sidebar.multiselect("Order status", ["Completed", "Pending", "Cancelled"], placeholder="All statuses")
ctypes = st.sidebar.multiselect("Customer type", sorted(df_all.Customer_Type.unique()), placeholder="All customer types")
regs = st.sidebar.multiselect("Region", sorted(df_all.Region.unique()), placeholder="All regions")
st.sidebar.caption(f"Report as-of date: **{AS_OF:%d %b %Y}**. 'Due' and 'overdue' are judged against this date.")
st.sidebar.caption("Empty filter = all values.")

d = df_all.copy()
if isinstance(dr, (list, tuple)) and len(dr) == 2:
    d = d[(d.Order_Date.dt.date >= dr[0]) & (d.Order_Date.dt.date <= dr[1])]
for col, sel in [("Product_Category", cats), ("Order_Status", stats), ("Customer_Type", ctypes), ("Region", regs)]:
    if sel:
        d = d[d[col].isin(sel)]
K = compute_kpis(d)


def pct(x):
    return "n/a" if x is None else f"{x*100:.1f}%"


def num(x, f="{:.1f}"):
    return "n/a" if x is None else f.format(x)


def card(col, label, value, sub, red=False):
    col.markdown(f'<div class="card{" red" if red else ""}"><div class="lab">{label}</div>'
                 f'<div class="val">{value}</div><div class="sub">{sub}</div></div>', unsafe_allow_html=True)


def style(fig, h=340):
    fig.update_layout(height=h, margin=dict(l=10, r=10, t=50, b=10), plot_bgcolor="white", paper_bgcolor="white",
                      font=dict(family="Arial", color=CHAR, size=12), legend=dict(orientation="h", y=-0.18, title=None),
                      title_font=dict(size=15))
    fig.update_xaxes(showgrid=False); fig.update_yaxes(gridcolor="#eceff1")
    return fig


# ------------------------------------------------------------------ landing
st.markdown('<div class="hero"><h1>Order Fulfilment & Installation Performance Dashboard</h1>'
            '<p>Business Operations Analytics Case Study · Neo Heat Pump — Sai Heating and Cooling Solutions · '
            f'Orders Jan–Jun 2026 · as of {AS_OF:%d %b %Y}</p></div>', unsafe_allow_html=True)
st.markdown('<div class="synthetic">⚠ SIMULATED DATA — 160 synthetic orders created for a portfolio case study. '
            'Figures do not describe the real orders, customers, prices or performance of the company.</div>',
            unsafe_allow_html=True)
if len(d) == 0:
    st.warning("No orders match these filters. Clear a filter in the sidebar.")
    st.stop()

tabs = st.tabs(["Overview", "Delivery", "Installation", "Pending & overdue", "Findings & recommendations", "Data & method"])

# ================================================================== OVERVIEW
with tabs[0]:
    st.markdown("**Business problem.** Management needs one reliable view of how many orders are completed, pending or "
                "cancelled, whether deliveries and installations keep their promised dates, which open orders are overdue, "
                "and where the process gets stuck.")
    c = st.columns(4)
    card(c[0], "Total orders", f"{K['total_orders']}", f"{K['completed']} completed · {K['pending']} pending · {K['cancelled']} cancelled")
    card(c[1], "Order completion rate", pct(K["order_completion_rate"]), "completed ÷ non-cancelled orders")
    card(c[2], "Open backlog", f"{K['backlog']}", f"₹{K['backlog_value']/1e5:,.0f} lakh open value (simulated)")
    card(c[3], "Overdue orders", f"{K['overdue_orders']}", f"{K['overdue_install_stage']} stuck at installation · {K['overdue_delivery_stage']} at delivery", red=True)
    st.write("")
    c = st.columns(4)
    card(c[0], "On-time delivery", pct(K["on_time_delivery_rate"]), f"{K['late_deliveries']} late of {K['deliveries_timed']} delivered")
    card(c[1], "Installation completion", pct(K["installation_completion_rate"]), f"{K['installs_due_done']} of {K['installs_due']} due installs done")
    card(c[2], "On-time installation", pct(K["on_time_install_rate"]), f"{K['late_installs']} late of {K['installs_timed']} installed")
    card(c[3], "Avg order cycle", f"{num(K['avg_order_cycle'])} d", f"order → installed · fulfilment {num(K['avg_order_to_delivery'])} d")
    st.write("")
    a, b = st.columns(2)
    sc = d.Order_Status.value_counts().reindex(["Completed", "Pending", "Cancelled"]).fillna(0).reset_index()
    sc.columns = ["Status", "Orders"]
    fig = px.bar(sc, x="Orders", y="Status", orientation="h", color="Status", color_discrete_map=STATUS_COLORS,
                 text="Orders", title="Order status distribution")
    fig.update_layout(showlegend=False); a.plotly_chart(style(fig), key="status")
    m = d.groupby([d.Order_Month.dt.strftime("%b"), "Order_Status"], sort=False).size().reset_index(name="Orders")
    m.columns = ["Month", "Status", "Orders"]
    order = [x for x in ["Jan", "Feb", "Mar", "Apr", "May", "Jun"] if x in m.Month.unique()]
    fig = px.bar(m, x="Month", y="Orders", color="Status", color_discrete_map=STATUS_COLORS, title="Monthly orders by current status",
                 category_orders={"Month": order, "Status": ["Completed", "Pending", "Cancelled"]})
    b.plotly_chart(style(fig), key="month")
    st.caption("June looks 'pending-heavy' because many June orders were not yet due on 30 Jun — that is normal, not a delay.")

# ================================================================== DELIVERY
with tabs[1]:
    c = st.columns(4)
    card(c[0], "Deliveries due", f"{K['deliveries_due']}", f"{K['deliveries_due_done']} delivered · completion {pct(K['delivery_completion_rate'])}")
    card(c[1], "On-time delivery rate", pct(K["on_time_delivery_rate"]), f"{K['on_time_deliveries']} on time or early")
    card(c[2], "Delayed deliveries", f"{K['late_deliveries']}", f"avg {num(K['avg_delivery_delay_late'])} days late · max {num(K['max_delivery_delay'], '{:.0f}')}", red=True)
    card(c[3], "Avg fulfilment time", f"{num(K['avg_order_to_delivery'])} d", f"production {num(K['avg_production'])} d · transit {num(K['avg_transit'])} d")
    st.write("")
    a, b = st.columns(2)
    t = d[d.Delivery_Timeliness != ""].groupby(["Product_Category", "Delivery_Timeliness"]).size().reset_index(name="Deliveries")
    fig = px.bar(t, y="Product_Category", x="Deliveries", color="Delivery_Timeliness", orientation="h",
                 color_discrete_map={"Early": GREEN, "On Time": TEAL, "Late": RED}, title="Delivery timeliness by product",
                 category_orders={"Delivery_Timeliness": ["Early", "On Time", "Late"]})
    fig.update_yaxes(title=None); a.plotly_chart(style(fig), key="deltime")
    g = by_group(d, "Product_Category")
    fig = px.bar(g.sort_values("On-time delivery %"), x="On-time delivery %", y="Product_Category", orientation="h",
                 text=g.sort_values("On-time delivery %")["On-time delivery %"].map(lambda v: "" if pd.isna(v) else f"{v:.0%}"),
                 title="On-time delivery rate by product")
    fig.update_traces(marker_color=TEAL); fig.update_xaxes(tickformat=".0%", range=[0, 1.05]); fig.update_yaxes(title=None)
    fig.add_vline(x=K["on_time_delivery_rate"] or 0, line_dash="dot", line_color=CHAR, annotation_text="overall")
    b.plotly_chart(style(fig), key="delrate")
    a, b = st.columns(2)
    late = d[d.Delivery_Delay_Days > 0].assign(Reason=lambda x: x.Delivery_Delay_Reason.replace("", "(not recorded)"))
    if len(late):
        r = late.groupby("Reason").agg(Late=("Order_ID", "count"), Avg_days=("Delivery_Delay_Days", "mean")).reset_index().sort_values("Late")
        fig = px.bar(r, x="Late", y="Reason", orientation="h", text="Late", title="Recorded reasons for late deliveries",
                     hover_data={"Avg_days": ":.1f"})
        fig.update_traces(marker_color=RED); fig.update_yaxes(title=None); a.plotly_chart(style(fig), key="delreason")
    rg = by_group(d, "Region")
    fig = px.bar(rg, x="Region", y="On-time delivery %", text=rg["On-time delivery %"].map(lambda v: "" if pd.isna(v) else f"{v:.0%}"),
                 title="On-time delivery rate by region")
    fig.update_traces(marker_color=CHAR); fig.update_yaxes(tickformat=".0%", range=[0, 1.05])
    b.plotly_chart(style(fig), key="delregion")
    st.caption("On-time rate = deliveries on or before the promised date ÷ delivered orders with valid dates. "
               "Undelivered and cancelled orders are not counted as on time or late.")

# ================================================================== INSTALLATION
with tabs[2]:
    c = st.columns(4)
    card(c[0], "Installations due", f"{K['installs_due']}", f"{K['installs_due_done']} completed")
    card(c[1], "Installation completion", pct(K["installation_completion_rate"]), "due installs done ÷ installs due")
    card(c[2], "On-time installation", pct(K["on_time_install_rate"]), f"{K['late_installs']} late · avg {num(K['avg_install_delay_late'])} d late")
    card(c[3], "Pending installations", f"{K['pending_installations']}", f"delivered, not installed · avg wait {num(K['avg_install_duration'])} d", red=True)
    st.write("")
    a, b = st.columns(2)
    act = d[d.Order_Status != "Cancelled"]
    status = pd.Series({
        "Installed on time": int((act.Install_Delay_Days <= 0).sum()),
        "Installed late": int((act.Install_Delay_Days > 0).sum()),
        "Installed – date issue": int(act.Installed.sum() - act.Install_Delay_Days.notna().sum()),
        "Awaiting install – overdue": int((act.Overdue_Stage == "Installation").sum()),
        "Awaiting install – on plan": int(((act.Current_Stage == "Awaiting Installation") & (act.Overdue_Stage != "Installation")).sum()),
        "Not yet delivered": int(act.Current_Stage.isin(["In Production", "In Transit"]).sum())}).reset_index()
    status.columns = ["Status", "Orders"]
    fig = px.bar(status, x="Orders", y="Status", orientation="h", text="Orders", title="Installation status (non-cancelled orders)",
                 color="Status", color_discrete_sequence=[TEAL, RED, GREY, RED, AMBER, "#b8c2ca"])
    fig.update_layout(showlegend=False); fig.update_yaxes(title=None, autorange="reversed"); a.plotly_chart(style(fig), key="inststat")
    # stage comparison
    stg = pd.DataFrame({"Stage": ["Production (order→dispatch)", "Transit (dispatch→delivery)", "Install wait (delivery→installed)"],
                        "Avg days": [K["avg_production"], K["avg_transit"], K["avg_install_duration"]]})
    fig = px.bar(stg, x="Stage", y="Avg days", text=stg["Avg days"].map(lambda v: "" if v is None else f"{v:.1f}"),
                 title="Average days per stage (operational delay analysis)")
    fig.update_traces(marker_color=AMBER); fig.update_xaxes(title=None, tickangle=0)
    fig.update_xaxes(ticktext=["Production", "Transit", "Delivery→Install"], tickvals=stg["Stage"])
    b.plotly_chart(style(fig), key="stage")
    a, b = st.columns(2)
    li = d[d.Install_Delay_Days > 0].assign(Reason=lambda x: x.Installation_Delay_Reason.replace("", "(not recorded)"))
    if len(li):
        r = li.groupby("Reason").size().reset_index(name="Late").sort_values("Late")
        fig = px.bar(r, x="Late", y="Reason", orientation="h", text="Late", title="Recorded reasons for late installations")
        fig.update_traces(marker_color=RED); fig.update_yaxes(title=None); a.plotly_chart(style(fig), key="instreason")
    split = pd.DataFrame({"Late installation after…": ["a LATE delivery (knock-on)", "an ON-TIME delivery"],
                          "Installations": [int(((d.Install_Delay_Days > 0) & (d.Delivery_Delay_Days > 0)).sum()),
                                            int(((d.Install_Delay_Days > 0) & (d.Delivery_Delay_Days <= 0)).sum())]})
    fig = px.bar(split, x="Late installation after…", y="Installations", text="Installations",
                 title="Is installation lateness caused by delivery?")
    fig.update_traces(marker_color=[GREY, RED]); b.plotly_chart(style(fig), key="knock")
    st.caption("Installation duration = days from delivery to installation. Rows with impossible dates "
               "(installed before delivery) are excluded from installation timing.")

# ================================================================== PENDING & OVERDUE
with tabs[3]:
    c = st.columns(3)
    card(c[0], "Open backlog", f"{K['backlog']}", f"₹{K['backlog_value']/1e5:,.0f} lakh (simulated)")
    card(c[1], "Overdue orders", f"{K['overdue_orders']}", f"avg {num(K['avg_days_overdue'], '{:.0f}')} days overdue · oldest {num(K['max_days_overdue'], '{:.0f}')}", red=True)
    card(c[2], "Not overdue yet", f"{K['backlog'] - K['overdue_orders']}", "open orders still within their promise")
    st.write("")
    pend = d[d.Order_Status == "Pending"].copy()
    pend["Status"] = pend.Overdue.map({1: "OVERDUE", 0: "within promise"})
    pend["Reason"] = pend.apply(lambda r: r.Installation_Delay_Reason if r.Overdue_Stage == "Installation" else r.Delivery_Delay_Reason, axis=1).replace("", "(not recorded)")
    pend.loc[pend.Overdue == 0, "Reason"] = ""
    show = pend.sort_values(["Overdue", "Days_Overdue"], ascending=[False, False])[
        ["Order_ID", "Status", "Current_Stage", "Days_Overdue", "Product_Category", "Customer_Type", "Region",
         "Order_Date", "Expected_Delivery_Date", "Expected_Installation_Date", "Reason"]]
    st.markdown("**Open orders — overdue first.** This is the list an operations coordinator would chase today.")
    st.dataframe(show, hide_index=True, column_config={
        "Order_Date": st.column_config.DateColumn("Ordered", format="DD MMM"),
        "Expected_Delivery_Date": st.column_config.DateColumn("Delivery promise", format="DD MMM"),
        "Expected_Installation_Date": st.column_config.DateColumn("Install promise", format="DD MMM"),
        "Days_Overdue": st.column_config.NumberColumn("Days overdue"), "Current_Stage": "Stage",
        "Product_Category": "Product", "Customer_Type": "Customer", "Order_ID": "Order"})
    st.download_button("Download open-order list (CSV)", show.to_csv(index=False).encode(), "open_orders.csv", "text/csv")

# ================================================================== FINDINGS
with tabs[4]:
    k = K_ALL
    g = by_group(df_all, "Product_Category").set_index("Product_Category")
    rg = by_group(df_all, "Region").set_index("Region")
    big = df_all.Product_Category.isin(["Commercial Heat Pump", "Custom Requirement"])
    kb, kr = compute_kpis(df_all[big]), compute_kpis(df_all[~big])
    li = df_all[df_all.Install_Delay_Days > 0]
    st.info("Findings use the **full dataset** (filters ignored) and describe SIMULATED data. Some patterns were assumptions "
            "built into the simulation, so they demonstrate the method rather than reveal real causes.")
    findings = [
        ("1. About 1 in 4 deliveries missed its promised date",
         f"On-time delivery {pct(k['on_time_delivery_rate'])} ({k['on_time_deliveries']} of {k['deliveries_timed']}); "
         f"{k['late_deliveries']} late, {num(k['avg_delivery_delay_late'])} days late on average.",
         "Missed promises create follow-up work and customer frustration.", "Set category-specific promise dates (R3)."),
        ("2. Late deliveries concentrate in Commercial Heat Pumps and Custom Requirements",
         f"These two categories are on time {pct(kb['on_time_delivery_rate'])} vs {pct(kr['on_time_delivery_rate'])} for the other three, and "
         f"account for {kb['late_deliveries']} of {k['late_deliveries']} late deliveries. Average production: Custom "
         f"{g.loc['Custom Requirement','Avg production (d)']:.1f} d vs Water Heater {g.loc['Heat Pump Water Heater','Avg production (d)']:.1f} d.",
         "One standard lead time does not fit long, variable builds.", "Category-based promise dates (R3) and component checks at order acceptance (R4)."),
        ("3. Installation is the weakest stage",
         f"On-time installation {pct(k['on_time_install_rate'])} vs on-time delivery {pct(k['on_time_delivery_rate'])}; "
         f"installation completion {pct(k['installation_completion_rate'])} vs delivery completion {pct(k['delivery_completion_rate'])}.",
         "A delivered machine that is not installed does not yet serve the customer.", "Pre-installation readiness check (R2)."),
        ("4. Many late installations followed an on-time delivery",
         f"{int((li.Delivery_Delay_Days <= 0).sum())} of {len(li)} late installations came after an on-time delivery. Top recorded reason: "
         f"'Customer site not ready' ({int((li.Installation_Delay_Reason == 'Customer site not ready').sum())}).",
         "Installation scheduling — not only the factory — drives lateness (hypothesis supported by reason codes only).", "Book install slots only after site readiness is confirmed (R2, R7)."),
        ("5. Overdue work sits mainly at installation",
         f"{k['overdue_orders']} overdue orders: {k['overdue_install_stage']} at installation, {k['overdue_delivery_stage']} at delivery; "
         f"average {num(k['avg_days_overdue'], '{:.0f}')} days overdue, oldest {num(k['max_days_overdue'], '{:.0f}')} days.",
         "Old open orders tie up value and risk cancellation (risk not measured).", "Daily overdue / awaiting-installation review (R1)."),
        ("6. Production is the biggest share of cycle time",
         f"Production {num(k['avg_production'])} d, transit {num(k['avg_transit'])} d, delivery→installation {num(k['avg_install_duration'])} d; "
         f"end-to-end {num(k['avg_order_cycle'])} d.", "Capacity and material planning are the largest lever on cycle time.", "R3, R4."),
        ("7. Other States deliver on time less often (small sample)",
         f"Other States {pct(rg.loc['Other States','On-time delivery %'])} vs Bengaluru {pct(rg.loc['Bengaluru','On-time delivery %'])} "
         f"({int(rg.loc['Other States','Timed deliveries'])} timed deliveries).", "Transit allowances may be too tight.", "Review transit allowance (R9)."),
        ("8. Delay reasons are often missing",
         f"{k['late_del_noreason']} of {k['late_deliveries']} late deliveries and {k['late_inst_noreason']} of {k['late_installs']} late installations have no reason.",
         "Root-cause analysis is limited.", "Mandatory reason dropdown (R5)."),
    ]
    for t_, ev, why, act_ in findings:
        st.markdown(f'<div class="finding"><b class="t">{t_}</b><br><span style="color:{CHAR}">📊 {ev}</span><br>'
                    f'<span style="color:{GREY}">Why it matters: {why}</span><br><b>Action:</b> {act_}</div>', unsafe_allow_html=True)
    st.subheader("Recommendations (proposals — not implemented)")
    recs = pd.DataFrame([
        ("R1", "Daily review of overdue and delivered-not-installed orders (owner, next step, revised date)", "High", "Low", "Immediate", "Overdue orders; days overdue"),
        ("R2", "Pre-installation readiness check 3–5 days before delivery; book slot after readiness confirmed", "High", "Low", "2 weeks", "On-time installation rate"),
        ("R3", "Promise dates by product category based on actual production times", "High", "Medium", "1 month", "On-time delivery by category"),
        ("R4", "Component availability check at order acceptance for Custom/Commercial orders", "Medium", "Medium", "1–2 months", "Late deliveries – component shortage"),
        ("R5", "Mandatory delay-reason dropdown for every missed promise", "Medium", "Low", "2 weeks", "% late records with a reason"),
        ("R6", "One order tracker with standard statuses, real date fields and duplicate checks", "Medium", "Low", "1 month", "Rows with data-quality flags"),
        ("R7", "Shared technician calendar and peak-season capacity plan", "Medium", "Medium", "Before next peak", "Delivery→installation days"),
        ("R8", "Weekly operations KPI report from this dashboard/workbook", "Medium", "Low", "Start now", "Report issued weekly"),
        ("R9", "Review transit allowance for Other States", "Low", "Low", "1–2 months", "On-time delivery – Other States"),
    ], columns=["#", "Recommendation", "Impact", "Effort", "Urgency", "Metric to monitor"])
    st.dataframe(recs, hide_index=True)

# ================================================================== DATA & METHOD
with tabs[5]:
    st.markdown(f"""
**Data source.** 160 synthetic orders (1 Jan – 30 Jun 2026) generated by `scripts/01_generate_synthetic_data.py`
for a portfolio case study. Customer references are anonymous codes; order values are illustrative, not real prices.
The raw export (163 rows) deliberately contains realistic problems — 3 duplicate rows, spelling variants, text and impossible
dates, values typed as text, impossible date sequences — which were cleaned using documented rules.

**Method.** Raw export → cleaning & validation (cleaning log of every change) → derived columns (delays, stages, overdue flags)
→ KPIs with explicit numerators, denominators and exclusions → Excel workbook (formulas) and this dashboard
(same rules in `kpi_engine.py`) → independent reconciliation (`scripts/05_qa_checks.py`: 175 checks, 0 failures).

**Key rules.** Cancelled orders are excluded from delivery and installation KPIs. Orders whose promise falls after the
as-of date ({AS_OF:%d %b %Y}) are *not yet due*, never overdue. Rows with impossible dates are kept but excluded from the
timing metric they would distort.

**Limitations.** Simulated data; some patterns were assumed in the generator. Groups are small (17–49 timed deliveries per
product). No technician, cost or customer-satisfaction data, so causes are hypotheses, not proof.
""")
    st.metric("Rows with a data-quality flag (filtered view)", int((d.DQ_Flag != "OK").sum()))
    with st.expander("Show filtered cleaned data"):
        st.dataframe(d, hide_index=True)
    st.download_button("Download filtered data (CSV)", d.to_csv(index=False).encode(), "filtered_orders.csv", "text/csv")

st.caption("Portfolio project by [Your Name] · Simulated data · Source code and Excel workbook in the GitHub repository.")
