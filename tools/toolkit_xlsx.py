"""Bygger Print to Profit-verktygslådan (xlsx). Kör: python3 tools/toolkit_xlsx.py"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from pathlib import Path
OUT = Path(__file__).resolve().parent.parent / "private/files/print-to-profit-toolkit.xlsx"
F = "Arial"
H = Font(name=F, bold=True, color="FFFFFF"); HF = PatternFill("solid", fgColor="16161A")
IN = Font(name=F, color="0000FF"); YF = PatternFill("solid", fgColor="FFF4C2")
N = Font(name=F); B = Font(name=F, bold=True); T = Font(name=F, bold=True, size=16)
G = Font(name=F, color="5E6169", italic=True)
thin = Border(bottom=Side(style="thin", color="E2E2E6"))
USD = '$#,##0.00;($#,##0.00);"-"'

wb = Workbook()
def sheet(name, first=False):
    ws = wb.active if first else wb.create_sheet(name); ws.title = name
    ws.sheet_view.showGridLines = False; return ws
def head(ws, row, cols):
    for i, c in enumerate(cols, 1):
        x = ws.cell(row, i, c); x.font = H; x.fill = HF; x.alignment = Alignment(wrap_text=True, vertical="center")
    ws.row_dimensions[row].height = 32
def inp(c, v, fmt=None):
    c.value = v; c.font = IN; c.fill = YF
    if fmt: c.number_format = fmt
def frm(c, v, fmt=USD, bold=False):
    c.value = v; c.font = B if bold else N; c.number_format = fmt

# Start here
ws = sheet("Start here", True)
ws["A1"] = "Print to Profit toolkit"; ws["A1"].font = T
rows = [
 "How to use it:",
 "1. Settings: fill in your own numbers once (yellow cells).",
 "2. Pricing: one row per product. Fill in the yellow cells, the rest calculates.",
 "3. Ideas: score your product ideas before you design anything (chapter 2).",
 "4. Shipping: weigh and measure each product packed, compare carriers (chapter 8).",
 "5. Monthly: your numbers every month, so you know what really pays (chapter 10).",
 "",
 "Yellow cell with blue text = you fill it in. Everything else is a formula, don't type over it.",
 "Row 1 in each tab is the example from the guide (the Switch game card holder). Overwrite it with your own.",
 "Google Sheets: File → Import → Upload this file. All formulas work there too.",
 "",
 "boredprinter.com · Print to Profit",
]
for i, t in enumerate(rows, 3):
    c = ws.cell(i, 1, t); c.font = B if t.endswith(":") else (G if t.startswith("boredprinter") else N)
ws.column_dimensions["A"].width = 100

# Settings
ws = sheet("Settings")
ws["A1"] = "Settings"; ws["A1"].font = T
ws["A2"] = "Your numbers. Used by the Pricing tab."; ws["A2"].font = G
S = [
 ("Spool price ($)", 20, USD, "What you pay for one spool"),
 ("Spool weight (g)", 1000, "#,##0", "Usually 1,000 g"),
 ("Waste buffer", 0.10, "0%", "Failed prints and purge. 10% is a safe start"),
 ("Printer power (W)", 120, "#,##0", "Most home printers use 100–150 W"),
 ("Electricity price ($/kWh)", 0.25, USD, "From your power bill"),
 ("Machine wear ($/print hour)", 0.25, USD, "Nozzles, plates, belts, one day a new printer. $0.20–0.40"),
 ("Your hourly rate ($)", 20, USD, "What you'd accept for a side job"),
 ("Markup", 2.5, '0.0"x"', "2 to 3. Your costs only get you to zero"),
 ("Marketplace fees (%)", 0.10, "0.0%", "Etsy is roughly 9–10% in total (transaction + payment). Check your country"),
 ("Fixed fee per sale ($)", 0.45, USD, "Listing fee + fixed payment fee"),
]
head(ws, 4, ["Setting", "Value", "Note"])
for i, (k, v, f, n) in enumerate(S, 5):
    ws.cell(i, 1, k).font = N; inp(ws.cell(i, 2), v, f); ws.cell(i, 3, n).font = G
ws.column_dimensions["A"].width = 32; ws.column_dimensions["B"].width = 14; ws.column_dimensions["C"].width = 70
R = {k: f"Settings!$B${i}" for i, (k, *_ ) in enumerate(S, 5)}
sp, sw, wb_, pw, kwh, mach, rate, mk, fee, fix = (R[s[0]] for s in S)

# Pricing
ws = sheet("Pricing")
ws["A1"] = "Pricing"; ws["A1"].font = T
ws["A2"] = "One row per product. Fill in the yellow cells. Suggested price includes fees, so the profit is what you keep."; ws["A2"].font = G
cols = ["Product", "Grams (slicer)", "Print hours", "Hands-on minutes", "Packaging ($)", "Material", "Power", "Machine", "Your time",
        "Total cost", "Suggested price", "Your price", "Fees", "Profit per sale", "Profit per hands-on hour"]
head(ws, 4, cols)
for r in range(5, 25):
    ex = r == 5
    inp(ws.cell(r, 1), "Switch game card holder (example)" if ex else None)
    inp(ws.cell(r, 2), 45 if ex else None, "#,##0")
    inp(ws.cell(r, 3), 2 if ex else None, "0.0")
    inp(ws.cell(r, 4), 10 if ex else None, "#,##0")
    inp(ws.cell(r, 5), 1 if ex else None, USD)
    inp(ws.cell(r, 12), 17 if ex else None, USD)
    g = f'IF($A{r}="","",'
    frm(ws.cell(r, 6), f"={g}{sp}/{sw}*B{r}*(1+{wb_}))")
    frm(ws.cell(r, 7), f"={g}{pw}/1000*C{r}*{kwh})")
    frm(ws.cell(r, 8), f"={g}C{r}*{mach})")
    frm(ws.cell(r, 9), f"={g}D{r}/60*{rate})")
    frm(ws.cell(r, 10), f"={g}SUM(E{r}:I{r}))", bold=True)
    frm(ws.cell(r, 11), f"={g}(J{r}*{mk}+{fix})/(1-{fee}))", bold=True)
    frm(ws.cell(r, 13), f'=IF(OR($A{r}="",L{r}=""),"",L{r}*{fee}+{fix})')
    frm(ws.cell(r, 14), f'=IF(OR($A{r}="",L{r}=""),"",L{r}-M{r}-SUM(E{r}:H{r}))', bold=True)
    frm(ws.cell(r, 15), f'=IF(OR($A{r}="",L{r}="",D{r}=0),"",N{r}/(D{r}/60))')
    for c in range(1, 16): ws.cell(r, c).border = thin
ws.cell(26, 1, "Profit per sale = your price minus fees and all costs except your time. Profit per hands-on hour shows what you really earn for your work.").font = G
ws.column_dimensions["A"].width = 34
for c in "BCDEFGHIJKLMNO": ws.column_dimensions[c].width = 13
ws.freeze_panes = "B5"

# Ideas
ws = sheet("Ideas")
ws["A1"] = "Idea scoring"; ws["A1"].font = T
ws["A2"] = "Score each idea 1–5 (5 = best). Design the one with the highest score first. Chapter 2."; ws["A2"].font = G
head(ws, 4, ["Idea", "Buyer (who exactly?)", "Proof of demand", "Few good competitors", "Easy to design", "Cheap to ship", "Can be personalized", "Score /10", "Notes"])
dv = DataValidation(type="whole", operator="between", formula1="1", formula2="5", allow_blank=True, showErrorMessage=True, error="Use 1 to 5")
ws.add_data_validation(dv)
ex = ["Switch game card holder (example)", "Switch players with loose game cards", 5, 3, 5, 5, 4, None, "~250 reviews on a top listing. Complaint: cards fall out."]
for r in range(5, 20):
    for c in range(1, 10):
        if c == 8: continue
        v = ex[c - 1] if r == 5 else None
        inp(ws.cell(r, c), v)
        if 3 <= c <= 7: dv.add(ws.cell(r, c))
    frm(ws.cell(r, 8), f'=IF(A{r}="","",ROUND(SUM(C{r}:G{r})/2.5,1))', "0.0", bold=True)
    for c in range(1, 10): ws.cell(r, c).border = thin
ws.column_dimensions["A"].width = 34; ws.column_dimensions["B"].width = 34; ws.column_dimensions["I"].width = 50
for c in "CDEFGH": ws.column_dimensions[c].width = 13
ws.freeze_panes = "B5"

# Shipping
ws = sheet("Shipping")
ws["A1"] = "Shipping"; ws["A1"].font = T
ws["A2"] = "Weigh and measure each product packed. Compare 2–3 carriers. Check your post's exact letter limits. Chapter 8."; ws["A2"].font = G
head(ws, 4, ["Product", "Packed weight (g)", "Length (mm)", "Width (mm)", "Height (mm)", "Under 25 mm?", "Carrier 1 ($)", "Carrier 2 ($)", "Carrier 3 ($)", "Cheapest"])
for r in range(5, 20):
    ex = r == 5
    vals = ["Switch game card holder (example)", 65, 115, 35, 20, None, None, None, None]
    for c in (1, 2, 3, 4, 5, 7, 8, 9):
        inp(ws.cell(r, c), vals[c - 1] if ex else None, "#,##0" if c <= 5 and c > 1 else (USD if c >= 7 else None))
    frm(ws.cell(r, 6), f'=IF(E{r}="","",IF(E{r}<=25,"Maybe a letter","Parcel"))', "@")
    frm(ws.cell(r, 10), f'=IF(COUNT(G{r}:I{r})=0,"",MIN(G{r}:I{r}))', USD, bold=True)
    for c in range(1, 11): ws.cell(r, c).border = thin
ws.column_dimensions["A"].width = 34
for c in "BCDEFGHIJ": ws.column_dimensions[c].width = 14
ws.freeze_panes = "B5"

# Monthly
ws = sheet("Monthly")
ws["A1"] = "Monthly numbers"; ws["A1"].font = T
ws["A2"] = "Fill in once a month. Profit per hour is the number that tells you if it's worth it. Chapter 10."; ws["A2"].font = G
head(ws, 4, ["Month", "Orders", "Revenue ($)", "Fees ($)", "Material + packaging ($)", "Shipping you paid ($)", "Ads and other ($)", "Profit ($)", "Hours worked", "Profit per hour", "Best channel"])
for r in range(5, 17):
    inp(ws.cell(r, 1), None, "@")
    for c in (2, 3, 4, 5, 6, 7, 9): inp(ws.cell(r, c), None, "#,##0" if c in (2,) else ("0.0" if c == 9 else USD))
    inp(ws.cell(r, 11), None)
    frm(ws.cell(r, 8), f'=IF(C{r}="","",C{r}-SUM(D{r}:G{r}))', USD, bold=True)
    frm(ws.cell(r, 10), f'=IF(OR(H{r}="",I{r}="",I{r}=0),"",H{r}/I{r})', USD)
    for c in range(1, 12): ws.cell(r, c).border = thin
ws.cell(17, 1, "Total").font = B
for c, f in ((2, "#,##0"), (3, USD), (4, USD), (5, USD), (6, USD), (7, USD), (8, USD), (9, "0.0")):
    L = "ABCDEFGHIJK"[c - 1]; frm(ws.cell(17, c), f"=SUM({L}5:{L}16)", f, bold=True)
frm(ws.cell(17, 10), '=IF(I17=0,"",H17/I17)', USD, bold=True)
ws.column_dimensions["A"].width = 14
for c in "BCDEFGHIJ": ws.column_dimensions[c].width = 14
ws.column_dimensions["K"].width = 24
wb.save(OUT); print(OUT)
