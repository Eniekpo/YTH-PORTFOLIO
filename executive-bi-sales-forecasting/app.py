from __future__ import annotations

from pathlib import Path
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.analytics import calculate_kpis, filter_sales, monthly_performance, rfm_segmentation, yoy_growth
from src.config import COMPANY_NAME, CURRENCY_SYMBOL, DB_PATH, DEFAULT_FORECAST_MONTHS
from src.database import query_df
from src.forecasting import forecast_monthly_revenue

st.set_page_config(
    page_title="Executive BI & Sales Forecasting",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
    div[data-testid="stMetric"] {background: rgba(120,120,120,0.06); border: 1px solid rgba(120,120,120,0.14); padding: 0.8rem 1rem; border-radius: 12px;}
    .small-note {font-size: 0.86rem; opacity: 0.75;}
    </style>
    """,
    unsafe_allow_html=True,
)


def money(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"{CURRENCY_SYMBOL}{value/1_000_000:,.2f}M"
    if abs(value) >= 1_000:
        return f"{CURRENCY_SYMBOL}{value/1_000:,.1f}K"
    return f"{CURRENCY_SYMBOL}{value:,.0f}"


@st.cache_data(show_spinner=False)
def load_sales() -> pd.DataFrame:
    return query_df("SELECT * FROM vw_sales_enriched")


@st.cache_data(show_spinner=False)
def load_data_quality() -> dict:
    with sqlite3.connect(DB_PATH) as conn:
        sales = pd.read_sql_query("SELECT * FROM fact_sales", conn)
        customers = pd.read_sql_query("SELECT * FROM dim_customer", conn)
        products = pd.read_sql_query("SELECT * FROM dim_product", conn)
    return {
        "sales_rows": len(sales),
        "customers": len(customers),
        "products": len(products),
        "missing_sales": int(sales.isna().sum().sum()),
        "duplicate_lines": int(sales.duplicated().sum()),
        "negative_net_sales": int((sales["net_sales"] < 0).sum()),
        "invalid_margin_rows": int((sales["gross_profit"] > sales["net_sales"]).sum()),
    }


if not DB_PATH.exists():
    st.error("The analytical database has not been created yet.")
    st.code("python setup_project.py\nstreamlit run app.py", language="bash")
    st.stop()

sales = load_sales()
sales["order_date"] = pd.to_datetime(sales["order_date"])

st.title("Executive Business Intelligence & Sales Forecasting Platform")
st.caption(f"Portfolio case study for {COMPANY_NAME} · Synthetic data · SQL + Python + Streamlit + Forecasting")

with st.sidebar:
    st.header("Filters")
    min_date = sales["order_date"].min().date()
    max_date = sales["order_date"].max().date()
    date_range = st.date_input("Order date", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    region_options = sorted(sales["region"].dropna().unique())
    channel_options = sorted(sales["channel"].dropna().unique())
    category_options = sorted(sales["category"].dropna().unique())

    regions = st.multiselect("Region", region_options, default=region_options)
    channels = st.multiselect("Channel", channel_options, default=channel_options)
    categories = st.multiselect("Category", category_options, default=category_options)
    st.markdown("---")
    st.markdown("<div class='small-note'>Tip: narrow filters to explore regional, channel, or product performance.</div>", unsafe_allow_html=True)

filtered = filter_sales(sales, start_date, end_date, regions, channels, categories)
kpis = calculate_kpis(filtered)
monthly = monthly_performance(filtered)
growth = yoy_growth(monthly)

if filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Revenue", money(kpis["revenue"]), None if growth is None else f"{growth:.1%} YoY")
col2.metric("Gross Profit", money(kpis["gross_profit"]))
col3.metric("Gross Margin", f"{kpis['gross_margin']:.1%}")
col4.metric("Orders", f"{kpis['orders']:,}")
col5.metric("Average Order Value", money(kpis["aov"]))

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Executive Overview", "Sales Performance", "Customers", "Products", "Forecast", "Data Quality"
])

with tab1:
    left, right = st.columns([2, 1])
    with left:
        fig = px.line(monthly, x="month", y="revenue", markers=True, title="Monthly Revenue Trend")
        fig.update_layout(yaxis_title="Revenue", xaxis_title="", hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        region_perf = filtered.groupby("region", as_index=False).agg(revenue=("net_sales", "sum"), profit=("gross_profit", "sum"))
        region_perf = region_perf.sort_values("revenue", ascending=True)
        fig = px.bar(region_perf, x="revenue", y="region", orientation="h", title="Revenue by Region")
        fig.update_layout(xaxis_title="Revenue", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        channel_perf = filtered.groupby("channel", as_index=False)["net_sales"].sum().sort_values("net_sales", ascending=False)
        fig = px.pie(channel_perf, names="channel", values="net_sales", hole=0.55, title="Channel Mix")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        category_perf = filtered.groupby("category", as_index=False).agg(revenue=("net_sales", "sum"), profit=("gross_profit", "sum"))
        category_perf["margin"] = category_perf["profit"] / category_perf["revenue"]
        fig = px.scatter(category_perf, x="revenue", y="margin", size="profit", text="category", title="Category Revenue vs Margin")
        fig.update_traces(textposition="top center")
        fig.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)

    best_region = region_perf.sort_values("revenue", ascending=False).iloc[0]
    best_category = category_perf.sort_values("profit", ascending=False).iloc[0]
    st.info(
        f"Executive insight: {best_region['region']} leads revenue at {money(best_region['revenue'])}. "
        f"{best_category['category']} contributes the most gross profit at {money(best_category['profit'])}. "
        f"Current return rate is {kpis['return_rate']:.1%}."
    )

with tab2:
    st.subheader("Sales Performance")
    c1, c2 = st.columns(2)
    with c1:
        channel_month = filtered.copy()
        channel_month["month"] = channel_month["order_date"].dt.to_period("M").dt.to_timestamp()
        channel_month = channel_month.groupby(["month", "channel"], as_index=False)["net_sales"].sum()
        fig = px.area(channel_month, x="month", y="net_sales", color="channel", title="Revenue by Channel Over Time")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        country = filtered.groupby("country", as_index=False).agg(revenue=("net_sales", "sum"), orders=("order_id", "nunique"))
        country = country.sort_values("revenue", ascending=False)
        fig = px.bar(country, x="country", y="revenue", title="Country Performance")
        st.plotly_chart(fig, use_container_width=True)

    weekday = filtered.copy()
    weekday["weekday"] = pd.Categorical(
        weekday["order_date"].dt.day_name(),
        categories=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        ordered=True,
    )
    weekday = weekday.groupby("weekday", observed=False, as_index=False)["net_sales"].sum()
    fig = px.bar(weekday, x="weekday", y="net_sales", title="Revenue by Day of Week")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Customer Intelligence")
    rfm = rfm_segmentation(filtered)
    seg = rfm.groupby("segment", as_index=False).agg(customers=("customer_id", "count"), revenue=("monetary", "sum"))
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(seg.sort_values("customers", ascending=False), x="segment", y="customers", title="RFM Customer Segments")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.treemap(seg, path=["segment"], values="revenue", title="Revenue Contribution by RFM Segment")
        st.plotly_chart(fig, use_container_width=True)

    top_customers = (
        filtered.groupby(["customer_id", "customer_name", "customer_type", "region"], as_index=False)
        .agg(revenue=("net_sales", "sum"), orders=("order_id", "nunique"), gross_profit=("gross_profit", "sum"))
        .sort_values("revenue", ascending=False)
        .head(15)
    )
    st.dataframe(top_customers, use_container_width=True, hide_index=True)

with tab4:
    st.subheader("Product & Category Performance")
    prod = (
        filtered.groupby(["product_name", "category"], as_index=False)
        .agg(revenue=("net_sales", "sum"), gross_profit=("gross_profit", "sum"), units=("quantity", "sum"), returns=("return_amount", "sum"))
    )
    prod["margin"] = prod["gross_profit"] / prod["revenue"]
    prod["return_rate"] = prod["returns"] / (prod["revenue"] + prod["returns"])
    c1, c2 = st.columns(2)
    with c1:
        top_prod = prod.nlargest(12, "revenue").sort_values("revenue")
        fig = px.bar(top_prod, x="revenue", y="product_name", color="category", orientation="h", title="Top Products by Revenue")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.scatter(prod, x="margin", y="revenue", size="units", color="category", hover_name="product_name", title="Product Profitability Matrix")
        fig.update_xaxes(tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(prod.sort_values("revenue", ascending=False), use_container_width=True, hide_index=True)

with tab5:
    st.subheader("Revenue Forecast")
    st.caption("Forecasting is calculated from the currently filtered monthly revenue series.")
    horizon = st.slider("Forecast horizon (months)", min_value=3, max_value=12, value=DEFAULT_FORECAST_MONTHS)
    forecast, metrics = forecast_monthly_revenue(monthly, horizon)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=monthly["month"], y=monthly["revenue"], mode="lines+markers", name="Actual"))
    fig.add_trace(go.Scatter(x=forecast["month"], y=forecast["forecast"], mode="lines+markers", name="Forecast"))
    fig.add_trace(go.Scatter(
        x=list(forecast["month"]) + list(forecast["month"])[::-1],
        y=list(forecast["upper"]) + list(forecast["lower"])[::-1],
        fill="toself", line=dict(width=0), opacity=0.16, name="95% band", hoverinfo="skip"
    ))
    fig.update_layout(title="Monthly Revenue: Actual + Forecast", xaxis_title="", yaxis_title="Revenue", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    m1, m2, m3 = st.columns(3)
    m1.metric("Model", metrics["model"])
    m2.metric("In-sample MAE", "N/A" if metrics["mae"] is None else money(metrics["mae"]))
    m3.metric("In-sample MAPE", "N/A" if metrics["mape"] is None else f"{metrics['mape']:.1%}")
    st.dataframe(forecast, use_container_width=True, hide_index=True)
    st.caption("The confidence band is an indicative residual-based interval for portfolio demonstration, not a formal probabilistic forecast interval.")

with tab6:
    st.subheader("Data Quality & Pipeline Checks")
    dq = load_data_quality()
    c1, c2, c3 = st.columns(3)
    c1.metric("Fact rows", f"{dq['sales_rows']:,}")
    c2.metric("Customers", f"{dq['customers']:,}")
    c3.metric("Products", f"{dq['products']:,}")

    checks = pd.DataFrame([
        {"check": "Missing values in fact table", "issues": dq["missing_sales"]},
        {"check": "Duplicate fact rows", "issues": dq["duplicate_lines"]},
        {"check": "Negative net sales", "issues": dq["negative_net_sales"]},
        {"check": "Gross profit greater than net sales", "issues": dq["invalid_margin_rows"]},
    ])
    checks["status"] = checks["issues"].apply(lambda n: "PASS" if n == 0 else "REVIEW")
    st.dataframe(checks, use_container_width=True, hide_index=True)
    st.markdown(
        "This tab demonstrates an analytics-engineering mindset: dashboard outputs are accompanied by explicit quality checks, "
        "rather than assuming the input data is trustworthy."
    )

st.markdown("---")
st.caption("Portfolio project · Synthetic data only · Built to demonstrate SQL, Python analytics, BI design, customer segmentation, forecasting, and data-quality thinking.")
