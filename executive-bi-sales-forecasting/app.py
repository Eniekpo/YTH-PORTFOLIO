from __future__ import annotations

import sqlite3

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.analytics import (
    calculate_kpis,
    filter_sales,
    monthly_performance,
    rfm_segmentation,
    yoy_growth,
)
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
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #f8fafc 0%, #eef4ff 100%);
        color: #0f172a;
    }
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }
    .section-tag {
        display: inline-block;
        margin-bottom: 0.6rem;
        padding: 0.38rem 0.8rem;
        border-radius: 999px;
        background: #e0f2fe;
        border: 1px solid #bae6fd;
        color: #075985;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }
    .hero-copy {
        margin: 0.2rem 0 1rem;
        font-size: 1.08rem;
        color: #334155;
        line-height: 1.6;
    }
    .hero-copy strong {
        color: #0f172a;
        font-weight: 700;
    }
    .pill-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin: 0 0 1.5rem;
    }
    .pill {
        display: inline-flex;
        align-items: center;
        padding: 0.42rem 0.72rem;
        border-radius: 999px;
        background: #f1f5f9;
        border: 1px solid #dbeafe;
        color: #1d4ed8;
        font-size: 0.74rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid rgba(148, 163, 184, 0.32);
        padding: 1rem 1rem 0.8rem;
        border-radius: 16px;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.08);
    }
    [data-testid="stMetricLabel"] {
        color: #475569;
        font-size: 0.72rem;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    [data-testid="stMetricValue"] {
        font-size: clamp(1.5rem, 2vw, 2rem);
        font-weight: 700;
        color: #0f172a;
    }
    [data-testid="stMetricDelta"] {
        font-size: 0.8rem;
        color: #0f766e;
    }
    .small-note {
        font-size: 0.8rem;
        color: #475569;
        opacity: 0.9;
    }
    .stTabs [role="tablist"] {
        gap: 0.45rem;
        margin-bottom: 0.9rem;
    }
    .stTabs [role="tab"] {
        background: #f8fafc;
        color: #334155;
        border: 1px solid #dfe7f3;
        border-radius: 10px 10px 0 0;
        padding: 0.6rem 0.9rem;
        font-weight: 600;
    }
    .stTabs [role="tab"][aria-selected="true"] {
        background: #eff6ff;
        border-color: #bfdbfe;
        color: #1d4ed8;
    }
    .stDataFrame {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 12px;
        border: 1px solid #e2e8f0;
    }
    .stDataFrame table {
        color: #0f172a;
    }
    .stSidebar {
        background: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    .stSidebar .block-container {
        padding-top: 1rem;
    }
    .stAlert {
        background: #f8fafc;
        border: 1px solid #dbeafe;
        color: #0f172a;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def money(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"{CURRENCY_SYMBOL}{value / 1_000_000:,.2f}M"
    if abs(value) >= 1_000:
        return f"{CURRENCY_SYMBOL}{value / 1_000:,.1f}K"
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

st.markdown('<div class="section-tag">🚀 Portfolio Project</div>', unsafe_allow_html=True)
st.title("📊 Executive Business Intelligence & Sales Forecasting Platform")
st.markdown(
    '<div class="hero-copy"><strong>From 47,775 transaction lines</strong> to decision-ready insight for revenue, profitability, customer behaviour, and forecast planning.</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="pill-row">
      <span class="pill">🧠 SQL + Analytics Engineering</span>
      <span class="pill">🐍 Python + BI</span>
      <span class="pill">📈 Forecasting</span>
      <span class="pill">✅ Data Quality</span>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("🧰 Filters")
    min_date = sales["order_date"].min().date()
    max_date = sales["order_date"].max().date()
    date_range = st.date_input(
        "📅 Order date",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    region_options = sorted(sales["region"].dropna().unique())
    channel_options = sorted(sales["channel"].dropna().unique())
    category_options = sorted(sales["category"].dropna().unique())

    regions = st.multiselect("📍 Region", region_options, default=region_options)
    channels = st.multiselect("🛍️ Channel", channel_options, default=channel_options)
    categories = st.multiselect("📦 Category", category_options, default=category_options)
    st.markdown("---")
    st.markdown(
        "<div class='small-note'>Tip: narrow filters to explore regional, channel, or product performance.</div>",
        unsafe_allow_html=True,
    )

filtered = filter_sales(sales, start_date, end_date, regions, channels, categories)
kpis = calculate_kpis(filtered)
monthly = monthly_performance(filtered)
growth = yoy_growth(monthly)

if filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

metric_cols = st.columns(6)
metric_cols[0].metric("💰 Net Revenue", money(kpis["revenue"]), None if growth is None else f"{growth:.1%} YoY")
metric_cols[1].metric("📈 Gross Profit", money(kpis["gross_profit"]))
metric_cols[2].metric("📊 Gross Margin", f"{kpis['gross_margin']:.1%}")
metric_cols[3].metric("🧾 Orders", f"{kpis['orders']:,}")
metric_cols[4].metric("👥 Customers", f"{kpis['customers']:,}")
metric_cols[5].metric("🛒 Avg. Order Value", money(kpis["aov"]))

st.markdown("<div class='small-note'>📉 Return rate: <strong>{:.1%}</strong> · Synthetic data · {} · {} </div>".format(kpis["return_rate"], COMPANY_NAME, "SQL + Python + Streamlit"), unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Executive Overview",
    "📉 Performance Drivers",
    "👥 Customer Intelligence",
    "📈 Revenue Forecast",
    "✅ Trust & Delivery",
])

with tab1:
    left, right = st.columns([2, 1])
    with left:
        fig = px.line(monthly, x="month", y="revenue", markers=True, title="📈 Monthly Revenue Trend")
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#0f172a",
            yaxis_title="Revenue",
            xaxis_title="",
            hovermode="x unified",
            title_x=0.5,
        )
        st.plotly_chart(fig, use_container_width=True)
    with right:
        region_perf = filtered.groupby("region", as_index=False).agg(revenue=("net_sales", "sum"), profit=("gross_profit", "sum"))
        region_perf = region_perf.sort_values("revenue", ascending=True)
        fig = px.bar(region_perf, x="revenue", y="region", orientation="h", title="📍 Revenue by Region")
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#0f172a",
            xaxis_title="Revenue",
            yaxis_title="",
            title_x=0.5,
        )
        st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        channel_perf = filtered.groupby("channel", as_index=False)["net_sales"].sum().sort_values("net_sales", ascending=False)
        fig = px.pie(channel_perf, names="channel", values="net_sales", hole=0.5, title="🛍️ Channel Mix")
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#0f172a",
            title_x=0.5,
        )
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        category_perf = filtered.groupby("category", as_index=False).agg(revenue=("net_sales", "sum"), profit=("gross_profit", "sum"))
        category_perf["margin"] = category_perf["profit"] / category_perf["revenue"]
        fig = px.scatter(
            category_perf,
            x="revenue",
            y="margin",
            size="profit",
            text="category",
            title="📦 Category Revenue vs Margin",
        )
        fig.update_traces(textposition="top center")
        fig.update_yaxes(tickformat=".0%")
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#0f172a",
            title_x=0.5,
        )
        st.plotly_chart(fig, use_container_width=True)

    best_region = region_perf.sort_values("revenue", ascending=False).iloc[0]
    best_category = category_perf.sort_values("profit", ascending=False).iloc[0]
    st.info(
        f"Executive insight: {best_region['region']} leads revenue at {money(best_region['revenue'])}. "
        f"{best_category['category']} contributes the most gross profit at {money(best_category['profit'])}. "
        f"Current return rate is {kpis['return_rate']:.1%}."
    )

with tab2:
    st.subheader("📉 What is driving performance?")
    c1, c2 = st.columns(2)
    with c1:
        channel_month = filtered.copy()
        channel_month["month"] = channel_month["order_date"].dt.to_period("M").dt.to_timestamp()
        channel_month = channel_month.groupby(["month", "channel"], as_index=False)["net_sales"].sum()
        fig = px.area(channel_month, x="month", y="net_sales", color="channel", title="📊 Revenue by Channel Over Time")
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#0f172a",
            title_x=0.5,
        )
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        country = filtered.groupby("country", as_index=False).agg(revenue=("net_sales", "sum"), orders=("order_id", "nunique"))
        country = country.sort_values("revenue", ascending=False)
        fig = px.bar(country, x="country", y="revenue", title="🌍 Country Performance")
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#0f172a",
            title_x=0.5,
        )
        st.plotly_chart(fig, use_container_width=True)

    prod = (
        filtered.groupby(["product_name", "category"], as_index=False)
        .agg(revenue=("net_sales", "sum"), gross_profit=("gross_profit", "sum"), units=("quantity", "sum"), returns=("return_amount", "sum"))
    )
    prod["margin"] = prod["gross_profit"] / prod["revenue"]
    prod["return_rate"] = prod["returns"] / (prod["revenue"] + prod["returns"])
    c1, c2 = st.columns(2)
    with c1:
        top_prod = prod.nlargest(12, "revenue").sort_values("revenue")
        fig = px.bar(top_prod, x="revenue", y="product_name", color="category", orientation="h", title="🏆 Top Products by Revenue")
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#0f172a",
            title_x=0.5,
        )
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.scatter(prod, x="margin", y="revenue", size="units", color="category", hover_name="product_name", title="📦 Product Profitability Matrix")
        fig.update_xaxes(tickformat=".0%")
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#0f172a",
            title_x=0.5,
        )
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("👥 RFM segmentation turns purchase history into action")
    rfm = rfm_segmentation(filtered)
    seg = rfm.groupby("segment", as_index=False).agg(customers=("customer_id", "count"), revenue=("monetary", "sum"))
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(seg.sort_values("customers", ascending=False), x="segment", y="customers", title="🧑‍🤝‍🧑 Customer Segments")
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#0f172a",
            title_x=0.5,
        )
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.treemap(seg, path=["segment"], values="revenue", title="💸 Revenue Contribution by Segment")
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#0f172a",
            title_x=0.5,
        )
        st.plotly_chart(fig, use_container_width=True)

    top_customers = (
        filtered.groupby(["customer_id", "customer_name", "customer_type", "region"], as_index=False)
        .agg(revenue=("net_sales", "sum"), orders=("order_id", "nunique"), gross_profit=("gross_profit", "sum"))
        .sort_values("revenue", ascending=False)
        .head(15)
    )
    st.dataframe(top_customers, use_container_width=True, hide_index=True)

with tab4:
    st.subheader("📈 Revenue Forecast")
    st.caption("Forecasting is calculated from the currently filtered monthly revenue series.")
    horizon = st.slider("Forecast horizon (months)", min_value=3, max_value=12, value=DEFAULT_FORECAST_MONTHS)
    forecast, metrics = forecast_monthly_revenue(monthly, horizon)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=monthly["month"], y=monthly["revenue"], mode="lines+markers", name="Actual"))
    fig.add_trace(go.Scatter(x=forecast["month"], y=forecast["forecast"], mode="lines+markers", name="Forecast"))
    fig.add_trace(
        go.Scatter(
            x=list(forecast["month"]) + list(forecast["month"])[::-1],
            y=list(forecast["upper"]) + list(forecast["lower"])[::-1],
            fill="toself",
            line=dict(width=0),
            opacity=0.18,
            name="95% band",
            hoverinfo="skip",
        )
    )
    fig.update_layout(
        title="📉 Monthly Revenue: Actual + Forecast",
        xaxis_title="",
        yaxis_title="Revenue",
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#0f172a",
        title_x=0.5,
    )
    st.plotly_chart(fig, use_container_width=True)

    m1, m2, m3 = st.columns(3)
    m1.metric("🧠 Model", metrics["model"])
    m2.metric("📏 In-sample MAE", "N/A" if metrics["mae"] is None else money(metrics["mae"]))
    m3.metric("📐 In-sample MAPE", "N/A" if metrics["mape"] is None else f"{metrics['mape']:.1%}")
    st.dataframe(forecast, use_container_width=True, hide_index=True)
    st.caption(
        "The confidence band is an indicative residual-based interval for portfolio demonstration, "
        "not a formal probabilistic forecast interval."
    )

with tab5:
    st.subheader("✅ Trust & Delivery")
    dq = load_data_quality()
    c1, c2, c3 = st.columns(3)
    c1.metric("🧾 Fact rows", f"{dq['sales_rows']:,}")
    c2.metric("👥 Customers", f"{dq['customers']:,}")
    c3.metric("📦 Products", f"{dq['products']:,}")

    checks = pd.DataFrame(
        [
            {"check": "Missing values in fact table", "issues": dq["missing_sales"]},
            {"check": "Duplicate fact rows", "issues": dq["duplicate_lines"]},
            {"check": "Negative net sales", "issues": dq["negative_net_sales"]},
            {"check": "Gross profit greater than net sales", "issues": dq["invalid_margin_rows"]},
        ]
    )
    checks["status"] = checks["issues"].apply(lambda n: "PASS" if n == 0 else "REVIEW")
    st.dataframe(checks, use_container_width=True, hide_index=True)
    st.markdown(
        "This dashboard demonstrates an analytics-engineering mindset: data quality checks and tests are treated as part of the delivery workflow, "
        "not an afterthought."
    )

st.markdown("---")
st.caption(
    "Portfolio project · Synthetic data only · Built to demonstrate SQL, Python analytics, BI design, customer segmentation, forecasting, and data-quality thinking."
)
