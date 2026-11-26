import sqlite3
from pathlib import Path

db = sqlite3.connect(Path(__file__).resolve().parent / "nepse.db")

print("\n=== Snapshot: price vs 52-week range ===")
rows = db.execute("""
    SELECT symbol,
           CAST(ltp AS REAL),
           CAST(week_52_low AS REAL),
           CAST(week_52_high AS REAL),
           ROUND((CAST(ltp AS REAL) - CAST(week_52_low AS REAL)) / CAST(week_52_low AS REAL) * 100, 1),
           ROUND((CAST(week_52_high AS REAL) - CAST(ltp AS REAL)) / CAST(week_52_high AS REAL) * 100, 1),
           CAST(pe_ratio AS REAL),
           CAST(pb_ratio AS REAL)
    FROM snapshot
    ORDER BY 5 ASC
""").fetchall()
print("symbol | ltp | 52w low | 52w high | % above low | % below high | P/E | P/B")
for r in rows:
    print(" | ".join(str(x) for x in r))

print("\n=== Valuation history ===")
for r in db.execute("""
    SELECT symbol, date,
           ROUND(CAST(pe_ratio AS REAL), 1),
           ROUND(CAST(pb_ratio AS REAL), 2)
    FROM valuation
    ORDER BY symbol, date
"""):
    print(" | ".join(str(x) for x in r))

print("\n=== Quarterly metrics available ===")
for r in db.execute("""
    SELECT symbol, particular, COUNT(*)
    FROM quarterly
    GROUP BY symbol, particular
    ORDER BY symbol, particular
"""):
    print(" | ".join(str(x) for x in r))