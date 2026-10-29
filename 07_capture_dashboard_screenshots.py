"""Step 7 - Capture Streamlit dashboard screenshots for the README (needs the app running on localhost:8501)."""
import pathlib, time
from playwright.sync_api import sync_playwright
ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "screenshots"
shots = [("Overview", "dashboard_preview.png"), ("Delivery", "dashboard_delivery.png"), ("Installation", "dashboard_installation.png"),
         ("Pending & overdue", "dashboard_overdue.png"), ("Findings & recommendations", "dashboard_findings.png")]
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1440, "height": 1000}, device_scale_factor=1.5)
    pg.goto("http://localhost:8501", wait_until="networkidle"); pg.wait_for_selector("text=Order Fulfilment", timeout=60000); time.sleep(4)
    errs = pg.locator("[data-testid='stException']").count()
    print("exceptions on page:", errs)
    for tab, fn in shots:
        pg.get_by_role("tab", name=tab).click(); time.sleep(3)
        pg.screenshot(path=str(OUT / fn), full_page=True)
        print("captured", fn, "exceptions:", pg.locator("[data-testid='stException']").count())
    b.close()
