"""
Step 1 - Generate the SYNTHETIC raw order export.

Everything this script produces is SIMULATED for a portfolio case study.
It does not describe the real orders, customers, prices or performance of
Neo Heat Pump - Sai Heating and Cooling Solutions.

Design assumptions (built into the simulation, so findings that echo them are
NOT real-world discoveries):
  * Larger / custom products take longer to build than standard water heaters.
  * Orders going outside Karnataka spend longer in transit.
  * Some installations wait on the customer's site being ready, and technician
    capacity is tighter in May-June.
  * Pool heat pump orders peak in Feb-Apr.
  * About 6% of orders are cancelled.
A small number of realistic data-entry problems are injected on purpose so the
cleaning step has something real to fix (see INJECTED list at the bottom).

Run:  python scripts/01_generate_synthetic_data.py
"""
from datetime import date, timedelta
import random, csv, pathlib

SEED = 42
AS_OF = date(2026, 6, 30)          # report date: end of the 6-month review period
START = date(2026, 1, 1)
N_ORDERS = 160
OUT = pathlib.Path(__file__).resolve().parents[1] / "data" / "raw" / "raw_orders_export.csv"
rng = random.Random(SEED)

# category: weight, (min,max) unit value INR (illustrative only), promised lead days, production mean, sd
CATS = {
    "Heat Pump Water Heater":  (0.34, (85_000, 220_000), 10, 5, 2.5),
    "Commercial Heat Pump":    (0.25, (300_000, 1_200_000), 18, 15, 5),
    "Swimming Pool Heat Pump": (0.18, (200_000, 600_000), 14, 9, 3),
    "Heat Pump Dryer":         (0.12, (250_000, 800_000), 21, 17, 5),
    "Custom Requirement":      (0.11, (400_000, 1_500_000), 30, 28, 9),
}
CUST_TYPES = {
    "Heat Pump Water Heater":  [("Residential", .70), ("Commercial", .20), ("Institutional", .10)],
    "Commercial Heat Pump":    [("Commercial", .60), ("Institutional", .40)],
    "Swimming Pool Heat Pump": [("Residential", .45), ("Commercial", .55)],
    "Heat Pump Dryer":         [("Commercial", .80), ("Institutional", .20)],
    "Custom Requirement":      [("Commercial", .50), ("Institutional", .50)],
}
REGIONS = [("Bengaluru", .55, 0, (1, 2)), ("Rest of Karnataka", .27, 2, (2, 4)), ("Other States", .18, 4, (4, 9))]

def pick(pairs):
    r, acc = rng.random(), 0
    for item, w in pairs:
        acc += w
        if r <= acc:
            return item
    return pairs[-1][0]

def order_date(cat):
    # mild growth over the half-year; pool heat pumps peak Feb-Apr
    while True:
        d = START + timedelta(days=rng.randrange(0, (AS_OF - START).days - 2))
        w = 0.75 + 0.5 * (d - START).days / 180
        if cat == "Swimming Pool Heat Pump":
            w *= 1.8 if d.month in (2, 3, 4) else 0.6
        if rng.random() < w / 1.6:
            return d

def ddmmyyyy(d):
    return "" if d is None else d.strftime("%d-%m-%Y")

customers = [f"CUST-{n:04d}" for n in rng.sample(range(1000, 9999), 130)]
rows = []
for i in range(1, N_ORDERS + 1):
    cat = pick([(c, v[0]) for c, v in CATS.items()])
    _, (vmin, vmax), lead, pmean, psd = CATS[cat]
    ctype = pick(CUST_TYPES[cat])
    region, _, transit_allow, (tmin, tmax) = next(r for r in [pick([((x[0], x[1], x[2], x[3]), x[1]) for x in REGIONS])])
    od = order_date(cat)
    units = 1 if ctype == "Residential" else rng.choice([1, 1, 1, 2, 2, 3, 4]) if cat == "Commercial Heat Pump" else rng.choice([1, 1, 1, 2])
    value = round(rng.uniform(vmin, vmax) / 1000) * 1000 * units

    exp_del = od + timedelta(days=lead + transit_allow)
    prod = max(1, round(rng.gauss(pmean, psd)))
    del_reason = ""
    if rng.random() < 0.10 and cat in ("Custom Requirement", "Heat Pump Dryer", "Commercial Heat Pump"):
        prod += rng.randint(5, 14); del_reason = "Component shortage"
    stuck = None
    if date(2026, 3, 1) <= od <= date(2026, 6, 5) and rng.random() < 0.13:
        stuck = "component" if (cat != "Heat Pump Water Heater" and rng.random() < 0.4) else "site"
        if stuck == "component":
            prod += rng.randint(40, 75); del_reason = "Component shortage"
    dispatch = od + timedelta(days=prod)
    transit = rng.randint(tmin, tmax)
    if region == "Other States" and rng.random() < 0.25:
        transit += rng.randint(3, 6); del_reason = del_reason or "Transport scheduling"
    actual_del = dispatch + timedelta(days=transit)
    if actual_del > exp_del and not del_reason:
        del_reason = "Production backlog" if prod > lead * 0.8 else "Dispatch scheduling"

    install_window = 5 if cat in ("Commercial Heat Pump", "Custom Requirement", "Heat Pump Dryer") else 3
    exp_inst = exp_del + timedelta(days=install_window)
    lag = rng.randint(1, 3) + (2 if install_window == 5 else 0)
    inst_reason = ""
    r = rng.random()
    if r < 0.17:
        lag += rng.randint(5, 14); inst_reason = "Customer site not ready"
    elif r < 0.17 + (0.22 if od.month >= 5 else 0.08):
        lag += rng.randint(3, 7); inst_reason = "Technician availability"
    if stuck == "site":
        lag += rng.randint(35, 90); inst_reason = "Customer site not ready"
    actual_inst = actual_del + timedelta(days=lag)
    if actual_inst <= exp_inst:
        inst_reason = ""            # reason only kept when installation was actually late
    elif not inst_reason:
        inst_reason = "Knock-on from late delivery" if actual_del > exp_del else "Installation scheduling"
    if actual_del <= exp_del:
        del_reason = ""

    status, cancel_reason, note = "Completed", "", ""
    if rng.random() < 0.06:
        status = "Cancelled"
        cancel_reason = rng.choice(["Customer postponed project", "Price / budget", "Long lead time"])
        cancel_day = od + timedelta(days=rng.randint(2, 12))
        if dispatch > cancel_day: dispatch = None
        actual_del = actual_inst = None
        del_reason = inst_reason = ""
    else:
        if dispatch > AS_OF: dispatch = None
        if actual_del > AS_OF: actual_del = None
        if actual_inst > AS_OF: actual_inst = None
        if actual_inst is None:
            status = "Pending"
            # reasons are only known once the stage is late as of the report date
            if actual_del is None and exp_del >= AS_OF: del_reason = ""
            if exp_inst >= AS_OF or actual_del is None: inst_reason = ""
    # ~25% of late records have no reason entered (realistic gap)
    if del_reason and rng.random() < 0.25: del_reason = ""
    if inst_reason and rng.random() < 0.25: inst_reason = ""

    note = rng.choice(["", "", "", "Site survey done", "Customer requested weekend install",
                       "Replacement of old geyser", "Pipe routing confirmed", "Electrical load checked"])
    if status == "Pending" and inst_reason == "Customer site not ready":
        note = "Customer civil work in progress"
    rows.append(dict(order_id=f"NHP-{i:04d}", od=od, cust=rng.choice(customers), ctype=ctype, region=region,
                     cat=cat, units=units, value=value, exp_del=exp_del, dispatch=dispatch, del_=actual_del,
                     exp_inst=exp_inst, inst=actual_inst, status=status, del_reason=del_reason,
                     inst_reason=inst_reason, cancel_reason=cancel_reason, note=note))

# sort by order date so IDs follow entry order
rows.sort(key=lambda x: x["od"])
for n, r in enumerate(rows, 1):
    r["order_id"] = f"NHP-{n:04d}"

# a cancelled order that was already delivered and later returned (genuine, not an error)
canc = [r for r in rows if r["status"] == "Cancelled"]
if canc:
    c = canc[0]; c["dispatch"] = c["od"] + timedelta(days=8); c["del_"] = c["od"] + timedelta(days=10)
    c["cancel_reason"] = "Customer postponed project"; c["note"] = "Unit returned to factory after delivery"

# ---------------- convert to raw export strings ----------------
HEAD = ["Order ID", "Order Date", "Customer Ref", "Customer Type", "Region", "Product Category", "Units",
        "Order Value (INR)", "Expected Delivery", "Dispatch Date", "Delivery Date", "Expected Installation",
        "Installation Date", "Status", "Delivery Delay Reason", "Installation Delay Reason",
        "Cancellation Reason", "Notes"]
raw = []
for r in rows:
    raw.append([r["order_id"], ddmmyyyy(r["od"]), r["cust"], r["ctype"], r["region"], r["cat"], str(r["units"]),
                str(r["value"]), ddmmyyyy(r["exp_del"]), ddmmyyyy(r["dispatch"]), ddmmyyyy(r["del_"]),
                ddmmyyyy(r["exp_inst"]), ddmmyyyy(r["inst"]), r["status"], r["del_reason"], r["inst_reason"],
                r["cancel_reason"], r["note"]])

INJECTED = []
def inject(idx, col, val, why):
    INJECTED.append((raw[idx][0], HEAD[col], raw[idx][col], val, why)); raw[idx][col] = val

idx_by_status = lambda s: [k for k, x in enumerate(raw) if x[13] == s]
comp, pend, canc_i = idx_by_status("Completed"), idx_by_status("Pending"), idx_by_status("Cancelled")
rng2 = random.Random(7)
# 1. status spelling variants
for k, v in zip(rng2.sample(comp, 5), ["completed", "completed", "Complete", "Complete", "COMPLETED"]): inject(k, 13, v, "status variant")
for k, v in zip(rng2.sample(pend, 5), ["PENDING", "In Progress", "In Progress", "In Progress", "pending "]): inject(k, 13, v, "status variant")
for k in canc_i[1:3]: inject(k, 13, "Canceled", "status variant")
# 2. category / customer-type variants
cat_idx = lambda c: [k for k, x in enumerate(raw) if x[5] == c]
for k in rng2.sample(cat_idx("Swimming Pool Heat Pump"), 3): inject(k, 5, "Pool Heat Pump", "category variant")
for k in rng2.sample(cat_idx("Heat Pump Water Heater"), 3): inject(k, 5, "HP Water Heater", "category variant")
for k in rng2.sample(cat_idx("Commercial Heat Pump"), 2): inject(k, 5, "commercial heat pump", "category variant")
for k in rng2.sample([k for k, x in enumerate(raw) if x[3] == "Residential"], 2): inject(k, 3, "residential", "customer-type variant")
for k in rng2.sample([k for k, x in enumerate(raw) if x[3] == "Commercial"], 2): inject(k, 3, "Comm.", "customer-type variant")
# 3. whitespace in IDs
for k in rng2.sample(range(len(raw)), 4): inject(k, 0, " " + raw[k][0] + " ", "whitespace in ID")
# 4. alternative date format YYYY/MM/DD
for k in rng2.sample(comp, 6):
    d = raw[k][1]; inject(k, 1, f"{d[6:]}/{d[3:5]}/{d[:2]}", "date format variant")
# 5. impossible calendar date on a completed order's delivery date
bad = rng2.choice(comp); inject(bad, 10, "31-02-2026", "invalid date")
# 6. installation date earlier than delivery date (likely entry error) on 2 completed orders
for k in rng2.sample([c for c in comp if c != bad], 2):
    dd = raw[k][10]; dt = date(int(dd[6:]), int(dd[3:5]), int(dd[:2])) - timedelta(days=3)
    inject(k, 12, ddmmyyyy(dt), "install before delivery")
# 7. dispatch date before order date (typo)
k = rng2.choice([c for c in comp if raw[c][9]]); od_s = raw[k][1].replace("/", "-")
inject(k, 9, "01-01-2026" if not raw[k][1].startswith("01-01") else "31-12-2025", "dispatch before order")
# 8. completed order with installation date missing
k = rng2.choice([c for c in comp if raw[c][12] and c != bad]); inject(k, 12, "", "completed but no install date")
# 9. order value missing / typed as text with rupee symbol
for k in rng2.sample(range(len(raw)), 3): inject(k, 7, "", "missing value")
for k in rng2.sample(range(len(raw)), 2):
    v = int(raw[k][7] or 0)
    if v: inject(k, 7, f"Rs. {v:,}", "value as text")
# 10. three exact duplicate rows (double export)
dups = rng2.sample(range(len(raw)), 3)
for k in sorted(dups, reverse=True):
    raw.insert(k + 1, list(raw[k])); INJECTED.append((raw[k][0].strip(), "(whole row)", "", "", "duplicate row"))

OUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(HEAD); w.writerows(raw)
with open(OUT.parent / "injected_issues_reference.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["Order ID", "Field", "Original", "Injected value", "Issue"]); w.writerows(INJECTED)
print(f"wrote {len(raw)} raw rows ({N_ORDERS} unique orders) -> {OUT}")
print(f"injected issues: {len(INJECTED)}")
