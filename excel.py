import json
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter
from parsel import Selector

base = Path(__file__).resolve().parent
html_path = base / "rawa.html"

sel = Selector(text=html_path.read_text(encoding="utf-8", errors="ignore"))
props = json.loads(sel.css("div[data-page]::attr(data-page)").get())["props"]


def clean(v):
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False)
    return v


def autosize(ws):
    for col in ws.columns:
        width = max(len(str(c.value)) if c.value is not None else 0 for c in col)
        ws.column_dimensions[get_column_letter(col[0].column)].width = min(width + 2, 50)


def write_table(ws, rows):
    if not rows:
        ws.append(["No data"])
        return
    cols = []
    for r in rows:
        for k in r:
            if k not in cols:
                cols.append(k)
    ws.append(cols)
    for c in ws[1]:
        c.font = Font(bold=True)
    for r in rows:
        ws.append([clean(r.get(k)) for k in cols])
    ws.freeze_panes = "A2"
    autosize(ws)


wb = Workbook()

# Sheet 1: Summary (all single-value fields, grouped by section)
ws = wb.active
ws.title = "Summary"
ws.append(["Section", "Field", "Value"])
for c in ws[1]:
    c.font = Font(bold=True)
sections = [
    "stock_info", "latestPrice", "masterData", "funda_table",
    "stocksGenralInfo", "financialsEPS", "pe_pb_avg",
]
ws.append(["stock", "symbol", props.get("symbol")])
for sec in sections:
    data = props.get(sec) or {}
    for k, v in data.items():
        if isinstance(v, (dict, list)):
            continue
        ws.append([sec, k, v])
ws.freeze_panes = "A2"
autosize(ws)

# Sheet 2: Quarterly (long format)
q = props.get("quartesGrowths") or []
write_table(wb.create_sheet("Quarterly_Long"), q)

# Sheet 3: Quarterly pivot (one row per metric, one column per quarter)
quarters = {}
table = {}
for r in q:
    key = (r.get("financial_date"), f"{r.get('fiscal_year')} Q{r.get('quarter')}")
    quarters[key] = True
    table.setdefault(r.get("particulars"), {})[key] = r.get("value")
cols = sorted(quarters)
ws = wb.create_sheet("Quarterly_Pivot")
ws.append(["Metric"] + [f"{label} ({date})" for date, label in cols])
for c in ws[1]:
    c.font = Font(bold=True)
for metric, vals in sorted(table.items()):
    ws.append([metric] + [vals.get(k) for k in cols])
ws.freeze_panes = "B2"
autosize(ws)

# Sheet 4: Valuation history
write_table(wb.create_sheet("Valuation"), props.get("otherQuartGrowths") or [])

# Sheets for holdings (brokers, mutual funds), if present
for key, val in (props.get("otherHoldings") or {}).items():
    ws = wb.create_sheet(key[:30])
    if isinstance(val, list) and val and isinstance(val[0], dict):
        write_table(ws, val)
    elif isinstance(val, dict):
        write_table(ws, [{"field": k, "value": v} for k, v in val.items()])
    else:
        ws.append([key, clean(val)])

out = base / "rawa_data.xlsx"
wb.save(out)
print("Saved:", out)
print("Sheets:", wb.sheetnames)