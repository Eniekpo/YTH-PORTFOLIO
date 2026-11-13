# E-commerce Revenue Intelligence & Customer Analytics Platform

End-to-end portfolio project using UCI Online Retail II: Python ETL, transaction quality audit, revenue and product analytics, customer RFM segmentation, Streamlit dashboards, PostgreSQL schema/queries and automated tests.

## Dataset
Download Online Retail II from https://archive.ics.uci.edu/dataset/502/online+retail+ii . UCI reports 1,067,371 transaction lines from 1 Dec 2009 to 9 Dec 2011. The source workbook is about 43.5 MB and is not bundled in this ZIP. Dataset is CC BY 4.0. Citation: Chen, D. (2012). Online Retail II [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D.

Run `python download_data.py` or place the workbook at `data/raw/online_retail_II.xlsx`.

## Setup
```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python download_data.py
python run_pipeline.py
streamlit run app/Home.py
pytest -q
```
Dashboard pages: Executive Overview, Revenue & Orders, Product Intelligence, Customer Intelligence (RFM), Data Quality. You can upload the Excel/CSV source in the sidebar or use the local workbook.

## Definitions & caveats
Revenue is the sum of positive quantity × positive unit price for non-cancelled invoice lines. Cancellations (invoice starts with C), negative-quantity returns, invalid dates and invalid prices are excluded from positive-sales KPIs but counted in the audit. Missing customer IDs remain in overall revenue/product/country reporting but are excluded from RFM. Orders are distinct invoices. AOV = revenue / distinct invoices. RFM uses distinct invoice frequency, cumulative revenue and recency relative to the day after the latest dataset date. Gross profit/margin and predictive churn are NOT calculated: product costs are absent, and RFM segments are descriptive heuristics.
