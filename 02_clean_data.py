"""
Step 2 - Clean and validate the raw export.
Input : data/raw/raw_orders_export.csv   (never modified)
Output: data/processed/cleaned_orders.csv  (validated inputs + derived columns)
        data/processed/cleaning_log.csv    (every change, with the rule applied)
        data/processed/data_quality_checks.csv
Rules are documented in analysis/Data_Quality_Report.md.
"""
import pathlib, sys, re
import pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "dashboard"))
from kpi_engine import enrich, AS_OF

raw = pd.read_csv(ROOT / "data/raw/raw_orders_export.csv", dtype=str, keep_default_na=False)
log = []
def L(oid, field, before, after, rule):
    log.append(dict(Order_ID=oid, Field=field, Original_Value=before, Cleaned_Value=after, Rule=rule))

df = raw.copy()
checks = {"Raw rows received": len(raw)}
# R1 trim IDs
for i, v in df["Order ID"].items():
    if v != v.strip():
        L(v.strip(), "Order ID", repr(v), v.strip(), "R1 Trim leading/trailing spaces"); df.at[i, "Order ID"] = v.strip()
# R2 exact duplicates
dmask = df.duplicated(keep="first")
checks["Exact duplicate rows removed"] = int(dmask.sum())
for oid in df.loc[dmask, "Order ID"]:
    L(oid, "(whole row)", "duplicate copy", "removed", "R2 Remove exact duplicate row (kept first copy)")
df = df[~dmask].reset_index(drop=True)
checks["Duplicate Order IDs remaining"] = int(df["Order ID"].duplicated().sum())

# R3 standardise text categories
STATUS = {"completed": "Completed", "complete": "Completed", "pending": "Pending", "in progress": "Pending",
          "cancelled": "Cancelled", "canceled": "Cancelled"}
CAT = {"pool heat pump": "Swimming Pool Heat Pump", "hp water heater": "Heat Pump Water Heater"}
CT = {"comm.": "Commercial"}
def std(col, mapping, rule):
    for i, v in df[col].items():
        key = v.strip().lower()
        new = mapping.get(key) or next((c for c in VALID[col] if c.lower() == key), None)
        if new is None:
            L(df.at[i, "Order ID"], col, v, v, f"{rule} UNRECOGNISED - left as is, flagged")
        elif new != v:
            L(df.at[i, "Order ID"], col, v, new, rule); df.at[i, col] = new
VALID = {"Status": ["Completed", "Pending", "Cancelled"],
         "Product Category": ["Heat Pump Water Heater", "Commercial Heat Pump", "Swimming Pool Heat Pump",
                              "Heat Pump Dryer", "Custom Requirement"],
         "Customer Type": ["Residential", "Commercial", "Institutional"]}
std("Status", STATUS, "R3 Standardise status label ('In Progress' treated as Pending)")
std("Product Category", CAT, "R3 Standardise category name")
std("Customer Type", CT, "R3 Standardise customer type")

# R4 parse dates (DD-MM-YYYY standard; YYYY/MM/DD accepted); invalid -> blank + flag
DATE_MAP = {"Order Date": "Order_Date", "Expected Delivery": "Expected_Delivery_Date", "Dispatch Date": "Dispatch_Date",
            "Delivery Date": "Actual_Delivery_Date", "Expected Installation": "Expected_Installation_Date",
            "Installation Date": "Actual_Installation_Date"}
flags = {i: [] for i in df.index}
parsed = {}
for col in DATE_MAP:
    out = []
    for i, v in df[col].items():
        v = v.strip()
        if not v:
            out.append(pd.NaT); continue
        if re.fullmatch(r"\d{4}/\d{2}/\d{2}", v):
            d = pd.to_datetime(v, format="%Y/%m/%d", errors="coerce")
            if pd.notna(d): L(df.at[i, "Order ID"], col, v, d.strftime("%d-%m-%Y"), "R4 Convert YYYY/MM/DD to standard date")
        else:
            d = pd.to_datetime(v, format="%d-%m-%Y", errors="coerce")
        if pd.isna(d):
            L(df.at[i, "Order ID"], col, v, "(blank)", "R4 Invalid calendar date - set blank, row flagged, excluded from timing KPIs")
            flags[i].append(f"Invalid {col}")
        out.append(d)
    parsed[DATE_MAP[col]] = out

# R5 order value
vals = []
for i, v in df["Order Value (INR)"].items():
    s = v.strip()
    if not s:
        vals.append(None); flags[i].append("Order value missing"); 
        L(df.at[i, "Order ID"], "Order Value (INR)", "(blank)", "(blank)", "R5 Missing value kept blank - excluded from value KPIs only")
        continue
    num = re.sub(r"^(Rs\.?|INR|₹)\s*", "", s, flags=re.I).replace(",", "")
    if num != s:
        L(df.at[i, "Order ID"], "Order Value (INR)", s, num, "R5 Strip currency text and separators")
    vals.append(float(num))

c = pd.DataFrame({
    "Order_ID": df["Order ID"], **{k: v for k, v in parsed.items()},
    "Customer_Ref": df["Customer Ref"], "Customer_Type": df["Customer Type"], "Region": df["Region"],
    "Product_Category": df["Product Category"], "Units": df["Units"].astype(int), "Order_Value_INR": vals,
    "Order_Status": df["Status"], "Delivery_Delay_Reason": df["Delivery Delay Reason"],
    "Installation_Delay_Reason": df["Installation Delay Reason"], "Cancellation_Reason": df["Cancellation Reason"],
    "Operational_Notes": df["Notes"]})
c["Valid_Dispatch_Timing"] = 1; c["Valid_Delivery_Timing"] = 1; c["Valid_Install_Timing"] = 1

# R6 date-sequence and status-consistency checks (flag + exclude from affected metric; never overwrite)
for i, r in c.iterrows():
    oid = r.Order_ID
    if pd.notna(r.Dispatch_Date) and r.Dispatch_Date < r.Order_Date:
        flags[i].append("Dispatch before order date"); c.at[i, "Valid_Dispatch_Timing"] = 0
        L(oid, "Dispatch_Date", r.Dispatch_Date.strftime("%d-%m-%Y"), "unchanged", "R6 Impossible sequence - excluded from production/transit time")
    if pd.notna(r.Actual_Installation_Date) and pd.notna(r.Actual_Delivery_Date) and r.Actual_Installation_Date < r.Actual_Delivery_Date:
        flags[i].append("Installed before delivery"); c.at[i, "Valid_Install_Timing"] = 0
        L(oid, "Actual_Installation_Date", r.Actual_Installation_Date.strftime("%d-%m-%Y"), "unchanged", "R6 Impossible sequence - excluded from installation timing")
    if any("Invalid Delivery" in f for f in flags[i]):
        c.at[i, "Valid_Delivery_Timing"] = 0; c.at[i, "Valid_Dispatch_Timing"] = c.at[i, "Valid_Dispatch_Timing"]
    if r.Order_Status == "Completed" and pd.isna(r.Actual_Installation_Date):
        flags[i].append("Completed but installation date missing"); c.at[i, "Valid_Install_Timing"] = 0
        L(oid, "Actual_Installation_Date", "(blank)", "(blank)", "R7 Status kept as Completed (system of record); excluded from installation timing; confirm with installer")
    if r.Order_Status == "Cancelled" and pd.notna(r.Actual_Delivery_Date):
        flags[i].append("Cancelled after delivery (returned)"); c.at[i, "Valid_Delivery_Timing"] = 0
        L(oid, "Order_Status", "Cancelled", "Cancelled", "R8 Genuine cancellation after delivery - excluded from delivery KPIs, not counted as a failure")
    for a, b in [("Expected_Delivery_Date", "Order_Date"), ("Actual_Delivery_Date", "Order_Date"), ("Expected_Installation_Date", "Expected_Delivery_Date")]:
        if pd.notna(r[a]) and pd.notna(r[b]) and r[a] < r[b]:
            flags[i].append(f"{a} before {b}")
    for col in ["Actual_Delivery_Date", "Actual_Installation_Date", "Dispatch_Date"]:
        if pd.notna(r[col]) and r[col] > AS_OF:
            flags[i].append(f"{col} after report date")
    if r.Order_Status == "Pending" and pd.notna(r.Actual_Installation_Date):
        flags[i].append("Pending but installation date present")
c["DQ_Flag"] = [("; ".join(flags[i]) if flags[i] else "OK") for i in c.index]

# R9 late records without a reason (completeness, nothing changed)
e = enrich(c)
late_del_noreason = int(((e["Delivery_Delay_Days"] > 0) & (e["Delivery_Delay_Reason"].str.strip() == "")).sum())
late_inst_noreason = int(((e["Install_Delay_Days"] > 0) & (e["Installation_Delay_Reason"].str.strip() == "")).sum())

order = ["Order_ID", "Order_Date", "Customer_Ref", "Customer_Type", "Region", "Product_Category", "Units",
         "Order_Value_INR", "Expected_Delivery_Date", "Dispatch_Date", "Actual_Delivery_Date",
         "Expected_Installation_Date", "Actual_Installation_Date", "Order_Status", "Delivery_Delay_Reason",
         "Installation_Delay_Reason", "Cancellation_Reason", "Operational_Notes", "DQ_Flag",
         "Valid_Dispatch_Timing", "Valid_Delivery_Timing", "Valid_Install_Timing"]
c = c[order]
out = ROOT / "data/processed"; out.mkdir(parents=True, exist_ok=True)
enrich(c).to_csv(out / "cleaned_orders.csv", index=False, date_format="%Y-%m-%d")
pd.DataFrame(log).to_csv(out / "cleaning_log.csv", index=False)

checks.update({
    "Unique orders after cleaning": len(c),
    "Status values outside Completed/Pending/Cancelled": int((~c.Order_Status.isin(VALID["Status"])).sum()),
    "Category values outside standard list": int((~c.Product_Category.isin(VALID["Product Category"])).sum()),
    "Rows with at least one DQ flag": int((c.DQ_Flag != "OK").sum()),
    "Rows with missing order value": int(c.Order_Value_INR.isna().sum()),
    "Late deliveries with no reason recorded": late_del_noreason,
    "Late installations with no reason recorded": late_inst_noreason,
    "Cleaning log entries": len(log),
})
pd.DataFrame(list(checks.items()), columns=["Check", "Result"]).to_csv(out / "data_quality_checks.csv", index=False)
for k, v in checks.items(): print(f"{k}: {v}")
print(c.DQ_Flag.value_counts().to_string())
