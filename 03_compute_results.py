"""Step 3 - Independent Python calculation of every KPI and summary (used to QA the Excel workbook and to write the reports)."""
import sys, json, pathlib
import pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "dashboard"))
from kpi_engine import load, compute_kpis, by_group
d = load(ROOT / "data/processed/cleaned_orders.csv")
k = compute_kpis(d)
res = {"kpis": k}
for col in ["Product_Category", "Region", "Customer_Type"]:
    res[col] = by_group(d, col).round(4).to_dict(orient="records")
m = d.groupby(d.Order_Month.dt.strftime("%Y-%m"))
res["month"] = pd.DataFrame({"orders": m.size(), "completed": m.apply(lambda x: (x.Order_Status == "Completed").sum()),
    "pending": m.apply(lambda x: (x.Order_Status == "Pending").sum()), "cancelled": m.apply(lambda x: (x.Order_Status == "Cancelled").sum()),
    "on_time": m.apply(lambda x: (x.Delivery_Delay_Days <= 0).sum()), "late": m.apply(lambda x: (x.Delivery_Delay_Days > 0).sum())}).reset_index().to_dict(orient="records")
late_d = d[d.Delivery_Delay_Days > 0]; late_i = d[d.Install_Delay_Days > 0]
res["delivery_reasons"] = late_d.Delivery_Delay_Reason.replace("", "(not recorded)").value_counts().to_dict()
res["delivery_reason_avg"] = late_d.assign(r=late_d.Delivery_Delay_Reason.replace("", "(not recorded)")).groupby("r").Delivery_Delay_Days.mean().round(2).to_dict()
res["install_reasons"] = late_i.Installation_Delay_Reason.replace("", "(not recorded)").value_counts().to_dict()
res["install_reason_avg"] = late_i.assign(r=late_i.Installation_Delay_Reason.replace("", "(not recorded)")).groupby("r").Install_Delay_Days.mean().round(2).to_dict()
res["stage_counts"] = d.Current_Stage.value_counts().to_dict()
ov = d[d.Overdue == 1].sort_values("Days_Overdue", ascending=False)
res["overdue"] = ov[["Order_ID", "Product_Category", "Customer_Type", "Region", "Current_Stage", "Overdue_Stage", "Days_Overdue",
                     "Delivery_Delay_Reason", "Installation_Delay_Reason"]].fillna("").astype(str).to_dict(orient="records")
res["overdue_install_reasons"] = ov[ov.Overdue_Stage == "Installation"].Installation_Delay_Reason.replace("", "(not recorded)").value_counts().to_dict()
# late install split: knock-on vs installation-stage
res["late_install_knock_on"] = int((late_i.Delivery_Delay_Days > 0).sum())
res["late_install_with_ontime_delivery"] = int((late_i.Delivery_Delay_Days <= 0).sum())
res["late_install_delivery_unknown"] = int(late_i.Delivery_Delay_Days.isna().sum())
# component-heavy categories vs standard
big = d.Product_Category.isin(["Commercial Heat Pump", "Custom Requirement"])
res["big_vs_rest"] = {"big_on_time": compute_kpis(d[big])["on_time_delivery_rate"], "rest_on_time": compute_kpis(d[~big])["on_time_delivery_rate"],
                      "big_late": compute_kpis(d[big])["late_deliveries"], "all_late": k["late_deliveries"]}
(ROOT / "analysis").mkdir(exist_ok=True)
json.dump(res, open(ROOT / "analysis/results.json", "w"), indent=1, default=str)
print(json.dumps({x: res[x] for x in ["delivery_reasons","delivery_reason_avg","install_reasons","install_reason_avg","stage_counts","overdue_install_reasons","late_install_knock_on","late_install_with_ontime_delivery","late_install_delivery_unknown","big_vs_rest","month"]}, indent=0, default=str))
pd.set_option("display.width", 250)
print(pd.DataFrame(res["Customer_Type"]).to_string()); print(pd.DataFrame(res["overdue"]).to_string())
