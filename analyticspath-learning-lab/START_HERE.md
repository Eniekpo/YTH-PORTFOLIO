# Start Here

## Recommended order

1. Excel
2. SQL
3. Python
4. Power BI
5. Final Capstone

## Excel

Open:

```text
excel/AnalyticsPath_Excel_Lab.xlsx
```

Start on `Start_Here` and complete `Excel_Exercises` before consulting `Excel_Solutions`.

## SQL

Ready-to-query database:

```text
sql/analytics_lab.db
```

Start with:

```text
sql/02_exercises.sql
```

Then compare with:

```text
sql/03_solutions.sql
```

## Python

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Start Jupyter:

```bash
jupyter notebook
```

Open `python/01_python_analytics_starter.ipynb`.

## Power BI

Import:

```text
data/powerbi/retail_sales_powerbi.csv
```

Then follow `powerbi/POWER_BI_BUILD_GUIDE.md`.

## Learning Portal

```bash
streamlit run learning_portal/app.py
```

Normally opens at `http://localhost:8501`.

## Capstone

Read `assessments/CAPSTONE_BRIEF.md`.

## Automated checks

```bash
pytest -q
```
