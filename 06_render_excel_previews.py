"""Step 6 - Render the Excel dashboard and KPI sheet to PNG screenshots with LibreOffice (for the README)."""
import pathlib, subprocess, tempfile, shutil
import openpyxl
ROOT = pathlib.Path(__file__).resolve().parents[1]
tmp = pathlib.Path(tempfile.mkdtemp())
for sheet, name, area in [("OPERATIONS DASHBOARD", "excel_dashboard", None), ("KPI ANALYSIS", "kpi_analysis", "A1:J34")]:
    wb = openpyxl.load_workbook(ROOT / "excel/operations_analysis.xlsx")
    for ws in wb.worksheets:
        if ws.title != sheet: ws.sheet_state = "hidden"
    wb.active = wb.sheetnames.index(sheet); ws = wb[sheet]
    if area:
        ws.print_area = area; ws.page_setup.orientation = "landscape"
        ws.sheet_properties.pageSetUpPr.fitToPage = True; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 1
    wb.save(tmp / f"{name}.xlsx")
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(tmp), str(tmp / f"{name}.xlsx")], check=True, capture_output=True, timeout=180)
    subprocess.run(["pdftoppm", "-png", "-r", "150", "-f", "1", "-l", "1", "-singlefile", str(tmp / f"{name}.pdf"), str(tmp / name)], check=True)
    # trim white margins
    from PIL import Image, ImageChops
    im = Image.open(tmp / f"{name}.png").convert("RGB")
    bbox = ImageChops.difference(im, Image.new("RGB", im.size, "white")).getbbox()
    im.crop((max(0, bbox[0] - 20), max(0, bbox[1] - 20), min(im.width, bbox[2] + 20), min(im.height, bbox[3] + 20))).save(ROOT / "screenshots" / f"{name}.png", optimize=True)
    print("wrote screenshots/%s.png" % name)
shutil.rmtree(tmp)
