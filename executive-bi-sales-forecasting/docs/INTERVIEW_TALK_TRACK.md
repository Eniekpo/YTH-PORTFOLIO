# Interview Talk Track

## 30-second version

I built an end-to-end executive BI platform from raw synthetic transaction data. I modelled the data in SQLite using fact and dimension tables, wrote reusable SQL views, calculated executive KPIs in Python, added RFM customer segmentation and monthly revenue forecasting, and delivered the outputs in an interactive Streamlit dashboard. I also added data-quality checks and automated tests because I wanted the project to demonstrate reliable analytics engineering, not only visualisation.

## Strong points to explain in an interview

### Why a dimensional model?
A fact/dimension structure separates transactional events from descriptive customer and product attributes. This keeps business logic reusable and makes reporting queries easier to maintain.

### Why RFM?
RFM converts transaction history into commercially meaningful customer groups based on recency, frequency, and monetary value. It creates a bridge between analytics and retention action.

### Why Holt-Winters?
The synthetic sales series contains trend and seasonality. Holt-Winters is transparent, fast, and appropriate as an explainable baseline before moving to more complex forecasting approaches.

### Why include data-quality checks?
Executive reporting is only useful if the underlying data can be trusted. Missing values, duplicates, invalid sales, or broken profit relationships can materially change business decisions.

### What would you improve in production?
I would move the warehouse to PostgreSQL or a cloud warehouse, automate ingestion, add orchestration, introduce authentication and row-level security, implement forecast backtesting, add CI/CD, and monitor data-quality rules over time.
