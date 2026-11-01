from pathlib import Path
import csv
import json
import sqlite3

ROOT = Path(__file__).resolve().parents[1]

def test_raw_dataset():
    with (ROOT / "data/raw/retail_sales.csv").open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 1800
    assert len({r["Order_ID"] for r in rows}) == 1800

def test_powerbi_dataset():
    with (ROOT / "data/powerbi/retail_sales_powerbi.csv").open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        first = next(reader)
    required = {"Revenue","Cost","Profit","Profit_Margin","Year","Month","Year_Month"}
    assert required.issubset(first.keys())

def test_database_reconciles():
    con = sqlite3.connect(ROOT / "sql/analytics_lab.db")
    result = con.execute(
        "SELECT COUNT(*), ROUND(SUM(revenue),2), ROUND(SUM(profit),2), SUM(quantity) FROM sales"
    ).fetchone()
    con.close()
    assert result == (1800, 994444.64, 311406.63, 8151)

def test_notebooks_are_valid():
    for name in ["01_python_analytics_starter.ipynb", "02_python_analytics_solution.ipynb"]:
        nb = json.loads((ROOT / "python" / name).read_text(encoding="utf-8"))
        assert nb["nbformat"] == 4
        assert len(nb["cells"]) >= 10

def test_excel_workbook_exists():
    path = ROOT / "excel/AnalyticsPath_Excel_Lab.xlsx"
    assert path.exists()
    assert path.stat().st_size > 10000

def test_learning_materials_exist():
    expected = [
        ROOT / "powerbi/POWER_BI_BUILD_GUIDE.md",
        ROOT / "powerbi/DAX_MEASURES.md",
        ROOT / "assessments/CAPSTONE_BRIEF.md",
        ROOT / "learning_portal/app.py",
        ROOT / "docs/VALIDATION_RESULTS.md",
    ]
    assert all(p.exists() for p in expected)
