from pathlib import Path
import csv
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "powerbi" / "retail_sales_powerbi.csv"
TARGET = ROOT / "sql" / "analytics_lab.db"

def build():
    con = sqlite3.connect(TARGET)
    cur = con.cursor()
    cur.executescript("""
    DROP TABLE IF EXISTS sales;
    CREATE TABLE sales (
        order_id TEXT PRIMARY KEY,
        order_date TEXT NOT NULL,
        region TEXT NOT NULL,
        city TEXT NOT NULL,
        category TEXT NOT NULL,
        subcategory TEXT NOT NULL,
        product TEXT NOT NULL,
        customer_segment TEXT NOT NULL,
        channel TEXT NOT NULL,
        salesperson TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        unit_cost REAL NOT NULL,
        discount REAL NOT NULL,
        revenue REAL NOT NULL,
        cost REAL NOT NULL,
        profit REAL NOT NULL,
        profit_margin REAL NOT NULL,
        year INTEGER NOT NULL,
        month TEXT NOT NULL,
        year_month TEXT NOT NULL
    );
    """)

    with SOURCE.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = []
        for r in reader:
            rows.append([
                r["Order_ID"], r["Order_Date"], r["Region"], r["City"], r["Category"],
                r["Subcategory"], r["Product"], r["Customer_Segment"], r["Channel"],
                r["Salesperson"], int(r["Quantity"]), float(r["Unit_Price"]),
                float(r["Unit_Cost"]), float(r["Discount"]), float(r["Revenue"]),
                float(r["Cost"]), float(r["Profit"]), float(r["Profit_Margin"]),
                int(r["Year"]), r["Month"], r["Year_Month"]
            ])

    cur.executemany(
        "INSERT INTO sales VALUES (" + ",".join(["?"] * 21) + ")",
        rows
    )
    con.commit()
    con.close()
    print(f"Built {TARGET} with {len(rows)} rows.")

if __name__ == "__main__":
    build()
