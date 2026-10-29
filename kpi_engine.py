"""
KPI engine - one place where every KPI rule is defined.
Used by the Streamlit dashboard and by the QA script that cross-checks the Excel workbook.
All data is SYNTHETIC (simulated for a portfolio case study).
"""
from __future__ import annotations
import pandas as pd

AS_OF = pd.Timestamp("2026-06-30")
DATE_COLS = ["Order_Date", "Expected_Delivery_Date", "Dispatch_Date", "Actual_Delivery_Date",
             "Expected_Installation_Date", "Actual_Installation_Date"]


INPUT_COLS = ["Order_ID", "Order_Date", "Customer_Ref", "Customer_Type", "Region", "Product_Category", "Units",
              "Order_Value_INR", "Expected_Delivery_Date", "Dispatch_Date", "Actual_Delivery_Date",
              "Expected_Installation_Date", "Actual_Installation_Date", "Order_Status", "Delivery_Delay_Reason",
              "Installation_Delay_Reason", "Cancellation_Reason", "Operational_Notes", "DQ_Flag",
              "Valid_Dispatch_Timing", "Valid_Delivery_Timing", "Valid_Install_Timing"]


def load(path, as_of: pd.Timestamp = AS_OF) -> pd.DataFrame:
    """Read the cleaned CSV and (re)calculate every derived column from the validated inputs."""
    df = pd.read_csv(path, parse_dates=DATE_COLS, usecols=INPUT_COLS)
    for c in ["Delivery_Delay_Reason", "Installation_Delay_Reason", "Cancellation_Reason", "Operational_Notes"]:
        df[c] = df[c].fillna("")
    return enrich(df, as_of)


def enrich(df: pd.DataFrame, as_of: pd.Timestamp = AS_OF) -> pd.DataFrame:
    """Add the derived columns. Mirrors the formula columns in the Excel 'CLEANED DATA' sheet."""
    d = df.copy()
    canc = d["Order_Status"].eq("Cancelled")
    comp = d["Order_Status"].eq("Completed")
    pend = d["Order_Status"].eq("Pending")
    d["Order_Month"] = d["Order_Date"].dt.to_period("M").dt.to_timestamp()

    # --- delivery stage
    d["Delivery_Due"] = (~canc & (d["Expected_Delivery_Date"] <= as_of)).astype(int)
    d["Delivered"] = (~canc & (d["Actual_Delivery_Date"].notna() | comp)).astype(int)
    ok_del = d["Delivered"].eq(1) & d["Valid_Delivery_Timing"].eq(1) & d["Actual_Delivery_Date"].notna()
    d["Delivery_Delay_Days"] = (d["Actual_Delivery_Date"] - d["Expected_Delivery_Date"]).dt.days.where(ok_del)
    d["Delivery_Timeliness"] = pd.cut(d["Delivery_Delay_Days"], [-999, -1, 0, 999],
                                      labels=["Early", "On Time", "Late"]).astype(object).where(ok_del, "")
    # --- installation stage
    d["Install_Due"] = (~canc & (d["Expected_Installation_Date"] <= as_of)).astype(int)
    d["Installed"] = (~canc & (d["Actual_Installation_Date"].notna() | comp)).astype(int)
    ok_inst = d["Installed"].eq(1) & d["Valid_Install_Timing"].eq(1) & d["Actual_Installation_Date"].notna()
    d["Install_Delay_Days"] = (d["Actual_Installation_Date"] - d["Expected_Installation_Date"]).dt.days.where(ok_inst)
    d["Install_Timeliness"] = pd.cut(d["Install_Delay_Days"], [-999, -1, 0, 999],
                                     labels=["Early", "On Time", "Late"]).astype(object).where(ok_inst, "")
    # --- stage durations (days)
    ok_disp = d["Valid_Dispatch_Timing"].eq(1) & d["Dispatch_Date"].notna() & ~canc
    d["Production_Days"] = (d["Dispatch_Date"] - d["Order_Date"]).dt.days.where(ok_disp)
    d["Transit_Days"] = (d["Actual_Delivery_Date"] - d["Dispatch_Date"]).dt.days.where(ok_disp & ok_del)
    d["Install_Lead_Days"] = (d["Actual_Installation_Date"] - d["Actual_Delivery_Date"]).dt.days.where(ok_del & ok_inst)
    d["Order_To_Delivery_Days"] = (d["Actual_Delivery_Date"] - d["Order_Date"]).dt.days.where(ok_del)
    d["Order_Cycle_Days"] = (d["Actual_Installation_Date"] - d["Order_Date"]).dt.days.where(comp & ok_inst)
    # --- current stage & overdue
    stage = pd.Series("In Production", index=d.index)
    stage[d["Dispatch_Date"].notna()] = "In Transit"
    stage[d["Delivered"].eq(1)] = "Awaiting Installation"
    stage[comp] = "Completed"
    stage[canc] = "Cancelled"
    d["Current_Stage"] = stage
    od_del = pend & d["Delivered"].eq(0) & (d["Expected_Delivery_Date"] < as_of)
    od_inst = pend & d["Delivered"].eq(1) & (d["Expected_Installation_Date"] < as_of)
    d["Overdue"] = (od_del | od_inst).astype(int)
    d["Days_Overdue"] = pd.Series(pd.NA, index=d.index, dtype="Int64")
    d.loc[od_del, "Days_Overdue"] = (as_of - d.loc[od_del, "Expected_Delivery_Date"]).dt.days
    d.loc[od_inst, "Days_Overdue"] = (as_of - d.loc[od_inst, "Expected_Installation_Date"]).dt.days
    d["Overdue_Stage"] = ""
    d.loc[od_del, "Overdue_Stage"] = "Delivery"
    d.loc[od_inst, "Overdue_Stage"] = "Installation"
    return d


def _rate(n, dnm):
    return (n / dnm) if dnm else None


def compute_kpis(d: pd.DataFrame) -> dict:
    """Return KPI dictionary for an enriched (optionally filtered) dataframe."""
    k = {}
    k["total_orders"] = len(d)
    k["completed"] = int(d["Order_Status"].eq("Completed").sum())
    k["pending"] = int(d["Order_Status"].eq("Pending").sum())
    k["cancelled"] = int(d["Order_Status"].eq("Cancelled").sum())
    k["active_orders"] = k["total_orders"] - k["cancelled"]
    k["order_completion_rate"] = _rate(k["completed"], k["active_orders"])
    k["cancellation_rate"] = _rate(k["cancelled"], k["total_orders"])
    k["backlog"] = k["pending"]
    k["backlog_value"] = float(d.loc[d["Order_Status"].eq("Pending"), "Order_Value_INR"].sum())

    k["deliveries_due"] = int(d["Delivery_Due"].sum())
    k["deliveries_due_done"] = int((d["Delivery_Due"].eq(1) & d["Delivered"].eq(1)).sum())
    k["delivery_completion_rate"] = _rate(k["deliveries_due_done"], k["deliveries_due"])
    k["delivered"] = int(d["Delivered"].sum())
    timed = d["Delivery_Delay_Days"].notna()
    k["deliveries_timed"] = int(timed.sum())
    k["on_time_deliveries"] = int((d["Delivery_Delay_Days"] <= 0).sum())
    k["late_deliveries"] = int((d["Delivery_Delay_Days"] > 0).sum())
    k["on_time_delivery_rate"] = _rate(k["on_time_deliveries"], k["deliveries_timed"])
    late = d.loc[d["Delivery_Delay_Days"] > 0, "Delivery_Delay_Days"]
    k["avg_delivery_delay_late"] = float(late.mean()) if len(late) else None
    k["avg_delivery_delay_all"] = float(d["Delivery_Delay_Days"].mean()) if timed.any() else None
    k["max_delivery_delay"] = float(d["Delivery_Delay_Days"].max()) if timed.any() else None

    k["installs_due"] = int(d["Install_Due"].sum())
    k["installs_due_done"] = int((d["Install_Due"].eq(1) & d["Installed"].eq(1)).sum())
    k["installation_completion_rate"] = _rate(k["installs_due_done"], k["installs_due"])
    k["installed"] = int(d["Installed"].sum())
    k["pending_installations"] = int((d["Delivered"].eq(1) & d["Installed"].eq(0)).sum())
    ti = d["Install_Delay_Days"].notna()
    k["installs_timed"] = int(ti.sum())
    k["on_time_installs"] = int((d["Install_Delay_Days"] <= 0).sum())
    k["late_installs"] = int((d["Install_Delay_Days"] > 0).sum())
    k["on_time_install_rate"] = _rate(k["on_time_installs"], k["installs_timed"])
    li = d.loc[d["Install_Delay_Days"] > 0, "Install_Delay_Days"]
    k["avg_install_delay_late"] = float(li.mean()) if len(li) else None
    k["avg_install_duration"] = float(d["Install_Lead_Days"].mean()) if d["Install_Lead_Days"].notna().any() else None

    k["avg_order_to_delivery"] = float(d["Order_To_Delivery_Days"].mean()) if d["Order_To_Delivery_Days"].notna().any() else None
    k["avg_order_cycle"] = float(d["Order_Cycle_Days"].mean()) if d["Order_Cycle_Days"].notna().any() else None
    k["avg_production"] = float(d["Production_Days"].mean()) if d["Production_Days"].notna().any() else None
    k["avg_transit"] = float(d["Transit_Days"].mean()) if d["Transit_Days"].notna().any() else None
    k["overdue_orders"] = int(d["Overdue"].sum())
    k["overdue_delivery_stage"] = int((d["Overdue_Stage"] == "Delivery").sum())
    k["overdue_install_stage"] = int((d["Overdue_Stage"] == "Installation").sum())
    od = d["Days_Overdue"].dropna().astype(float)
    k["avg_days_overdue"] = float(od.mean()) if len(od) else None
    k["max_days_overdue"] = float(od.max()) if len(od) else None
    k["dq_rows"] = int((d["DQ_Flag"] != "OK").sum())
    k["late_del_noreason"] = int(((d["Delivery_Delay_Days"] > 0) & (d["Delivery_Delay_Reason"] == "")).sum())
    k["late_inst_noreason"] = int(((d["Install_Delay_Days"] > 0) & (d["Installation_Delay_Reason"] == "")).sum())
    k["orders_missing_value"] = int(d["Order_Value_INR"].isna().sum())
    act = ~d["Order_Status"].eq("Cancelled")
    k["total_order_value"] = float(d.loc[act, "Order_Value_INR"].sum())
    k["orders_with_value"] = int(d.loc[act, "Order_Value_INR"].notna().sum())
    k["completed_value"] = float(d.loc[d["Order_Status"].eq("Completed"), "Order_Value_INR"].sum())
    return k


def by_group(d: pd.DataFrame, col: str) -> pd.DataFrame:
    rows = []
    for g, sub in d.groupby(col, sort=True):
        k = compute_kpis(sub)
        rows.append({col: g, "Orders": k["total_orders"], "Completed": k["completed"], "Pending": k["pending"],
                     "Cancelled": k["cancelled"], "Timed deliveries": k["deliveries_timed"],
                     "On-time delivery %": k["on_time_delivery_rate"], "Late deliveries": k["late_deliveries"],
                     "Avg delay when late (d)": k["avg_delivery_delay_late"],
                     "On-time install %": k["on_time_install_rate"],
                     "Avg production (d)": k["avg_production"], "Avg cycle (d)": k["avg_order_cycle"],
                     "Overdue": k["overdue_orders"]})
    return pd.DataFrame(rows)
