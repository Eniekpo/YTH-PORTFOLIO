# E-commerce Revenue Intelligence & Customer Analytics Platform

End-to-end portfolio project using UCI Online Retail II: Python ETL, transaction quality audit, revenue and product analytics, customer RFM segmentation, Streamlit dashboards, PostgreSQL schema/queries and automated tests.

## Dataset
Download Online Retail II from https://archive.ics.uci.edu/dataset/502/online+retail+ii . UCI reports 1,067,371 transaction lines from 1 Dec 2009 to 9 Dec 2011. The source workbook is about 43.5 MB and is not bundled in this ZIP. Dataset is CC BY 4.0. Citation: Chen, D. (2012). Online Retail II [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D.

Run `python download_data.py` or place the workbook at `data/raw/online_retail_II.xlsx`.

## Run the dashboard

Create and activate a virtual environment, then install the project dependencies.

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app/Home.py
```

### Windows (PowerShell)

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app/Home.py
```

Streamlit opens the dashboard at `http://localhost:8501`. If that port is already in use, start it on another port:

```bash
python -m streamlit run app/Home.py --server.port 8502
```

The dashboard loads `data/raw/online_retail_II.xlsx` when present. Otherwise, use the sidebar uploader to select the UCI workbook or a compatible CSV. To download the source workbook into the expected location, run `python download_data.py` from the activated environment.

## Development setup

The data pipeline and tests are optional when you only want to open the dashboard:

```bash
python download_data.py
python run_pipeline.py
pytest -q
```

Dashboard pages: Executive Overview, Revenue & Orders, Product Intelligence, Customer Intelligence (RFM), Data Quality.

## Definitions & caveats
Revenue is the sum of positive quantity × positive unit price for non-cancelled invoice lines. Cancellations (invoice starts with C), negative-quantity returns, invalid dates and invalid prices are excluded from positive-sales KPIs but counted in the audit. Missing customer IDs remain in overall revenue/product/country reporting but are excluded from RFM. Orders are distinct invoices. AOV = revenue / distinct invoices. RFM uses distinct invoice frequency, cumulative revenue and recency relative to the day after the latest dataset date. Gross profit/margin and predictive churn are NOT calculated: product costs are absent, and RFM segments are descriptive heuristics.
