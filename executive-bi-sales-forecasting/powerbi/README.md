# Optional Power BI Companion

The Streamlit dashboard is the runnable application included with this repository. You can also use the generated CSV files to create a Power BI version of the same executive reporting model.

## Import these tables

- `data/raw/customers.csv` → `dim_customer`
- `data/raw/products.csv` → `dim_product`
- `data/raw/sales.csv` → `fact_sales`

## Relationships

- `dim_customer[customer_id]` 1 → * `fact_sales[customer_id]`
- `dim_product[product_id]` 1 → * `fact_sales[product_id]`
- Create a calendar table and link `Calendar[Date]` 1 → * `fact_sales[order_date]`

## Suggested report pages

1. Executive Overview
2. Regional & Channel Performance
3. Customer Intelligence
4. Product Profitability
5. Returns & Data Quality

## Suggested visuals

- KPI cards: Revenue, Gross Profit, Gross Margin, Orders, AOV
- Monthly revenue line chart
- Revenue by region bar chart
- Channel mix donut chart
- Category profitability scatter plot
- Product ranking table
- Customer segment chart

The file `measures.dax` contains a starter set of measures matching the KPI logic used by the Python dashboard.
