import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="YOLETECH Sales Dashboard",
    layout="wide"
)

st.title("Sales Performance Dashboard")
st.caption("Interactive Business Intelligence Report")

# Load dataset
file_path = Path("data/sales.csv")

if not file_path.exists():
    st.error("Sales CSV file not found.")
    st.stop()

df = pd.read_csv(file_path)

# Validate columns
required = [
    "Date", "Region", "Product",
    "Quantity", "Unit_Price"
]

missing = set(required) - set(df.columns)

if missing:
    st.error(f"Missing columns: {missing}")
    st.stop()

# Clean dataset
df["Date"] = pd.to_datetime(
    df["Date"], errors="coerce"
)

for col in ["Quantity", "Unit_Price"]:
    df[col] = pd.to_numeric(
        df[col], errors="coerce"
    )

df.dropna(subset=required, inplace=True)

df = df[
    (df["Quantity"] > 0) &
    (df["Unit_Price"] >= 0) &
    (df["Region"].str.strip() != "") &
    (df["Product"].str.strip() != "")
].copy()

df["Revenue"] = (
    df["Quantity"] * df["Unit_Price"]
)

if df.empty:
    st.warning("No valid sales records found.")
    st.stop()

# Sidebar filters
st.sidebar.header("Report Filters")

regions = st.sidebar.multiselect(
    "Select Region",
    sorted(df["Region"].unique()),
    default=sorted(df["Region"].unique())
)

products = st.sidebar.multiselect(
    "Select Product",
    sorted(df["Product"].unique()),
    default=sorted(df["Product"].unique())
)

filtered = df[
    df["Region"].isin(regions) &
    df["Product"].isin(products)
]

if filtered.empty:
    st.warning("No records match your filters.")
    st.stop()

# Calculate KPIs
revenue = filtered["Revenue"].sum()
transactions = len(filtered)
units = filtered["Quantity"].sum()
average_value = revenue / transactions

# KPI display
c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Revenue", f"₦{revenue:,.2f}")
c2.metric("Transactions", f"{transactions:,}")
c3.metric("Units Sold", f"{units:,}")
c4.metric("Average Transaction", f"₦{average_value:,.2f}")

st.divider()

# Regional performance
region_data = (
    filtered.groupby("Region", as_index=False)
    ["Revenue"].sum()
)

fig1 = px.bar(
    region_data,
    x="Region",
    y="Revenue",
    title="Revenue by Region",
    text_auto=".2s"
)

st.plotly_chart(fig1, use_container_width=True)

# Product performance
product_data = (
    filtered.groupby("Product", as_index=False)
    ["Revenue"].sum()
    .sort_values("Revenue", ascending=False)
)

fig2 = px.pie(
    product_data,
    names="Product",
    values="Revenue",
    title="Revenue by Product",
    hole=0.4
)

st.plotly_chart(fig2, use_container_width=True)

# Monthly revenue trend
monthly = filtered.copy()
monthly["Month"] = (
    monthly["Date"].dt.to_period("M").astype(str)
)

monthly_data = (
    monthly.groupby("Month", as_index=False)
    ["Revenue"].sum()
    .sort_values("Month")
)

fig3 = px.line(
    monthly_data,
    x="Month",
    y="Revenue",
    title="Monthly Revenue Trend",
    markers=True
)

st.plotly_chart(fig3, use_container_width=True)

# Transaction details
st.subheader("Sales Transactions")

st.dataframe(
    filtered.sort_values("Date", ascending=False),
    use_container_width=True
)

# Download report
csv_data = filtered.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "Download Sales Report",
    data=csv_data,
    file_name="sales_report.csv",
    mime="text/csv"
)