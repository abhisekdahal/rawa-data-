import csv
import sqlite3
from pathlib import Path

base = Path(__file__).resolve().parent
db = sqlite3.connect(base / "nepse.db")


def load(csv_name, table, key_cols):
    path = base / csv_name
    if not path.exists():
        print("Skipping, not found:", csv_name)
        return
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        print("Empty:", csv_name)
        return
    cols = list(rows[0].keys())
    db.execute(f"DROP TABLE IF EXISTS {table}")
    col_sql = ", ".join(f'"{c}"' for c in cols)
    unique = ", ".join(f'"{c}"' for c in key_cols)
    db.execute(f"CREATE TABLE {table} ({col_sql}, UNIQUE({unique}))")
    marks = ", ".join("?" for _ in cols)
    db.executemany(
        f"INSERT OR REPLACE INTO {table} VALUES ({marks})",
        [[r[c] for c in cols] for r in rows],
    )
    print(f"{table}: {len(rows)} rows")


load("stocks.csv", "snapshot", ["symbol", "as_of_utc"])
load("quarters.csv", "quarterly", ["symbol", "particular", "fiscal_year", "quarter"])
load("valuation.csv", "valuation", ["symbol", "date"])
db.commit()
db.close()