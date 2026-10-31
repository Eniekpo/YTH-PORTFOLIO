import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="YOLETECH Sales Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/YOLETECH/ps-dashboard#readme",
        "Report a bug": "https://github.com/YOLETECH/ps-dashboard/issues",
        "About": "## YOLETECH Sales Dashboard\nProfessional portfolio project demonstrating data cleaning, analysis, and interactive visualisation with Streamlit & Plotly."
    },
)

# ---------------------------------------------------------------------------
# Title & description
# ---------------------------------------------------------------------------
st.title("Sales Performance Dashboard")
st.caption("Interactive Business Intelligence Report – Portfolio Project")

# ---------------------------------------------------------------------------
# Load and clean data
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "sales.csv"
if not DATA_PATH.exists():
    st.error("⚠️ Sales CSV file not found.")
    st.stop()

raw_df = pd.read_csv(DATA_PATH)
# Expected columns
EXPECTED_COLS = ["Date", "Region", "Product", "Quantity", "Unit_Price"]
missing = set(EXPECTED_COLS) - set(raw_df.columns)
if missing:
    st.error(f"❌ Missing columns in dataset: {missing}")
    st.stop()

# Parse dates and numeric columns safely
df = raw_df.copy()
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
for col in ["Quantity", "Unit_Price"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")
# Drop rows with essential missing values
df.dropna(subset=EXPECTED_COLS, inplace=True)
# Filter out non‑positive values and whitespace entries
df = df[(df["Quantity"] > 0) & (df["Unit_Price"] > 0) & (df["Region"].str.strip() != "") & (df["Product"].str.strip() != "")]
# Compute revenue column
df["Revenue"] = df["Quantity"] * df["Unit_Price"]
if df.empty:
    st.warning("⚙️ No valid sales records after cleaning.")
    st.stop()

# ---------------------------------------------------------------------------
# Sidebar – filters
# ---------------------------------------------------------------------------
st.sidebar.header("Report Filters")
selected_regions = st.sidebar.multiselect(
    "Region",
    options=sorted(df["Region"].unique()),
    default=sorted(df["Region"].unique()),
)
selected_products = st.sidebar.multiselect(
    "Product",
    options=sorted(df["Product"].unique()),
    default=sorted(df["Product"].unique()),
)
# Apply filters
filtered = df[df["Region"].isin(selected_regions) & df["Product"].isin(selected_products)]
if filtered.empty:
    st.info("🔎 No records match the current filter selection.")
    st.stop()

# ---------------------------------------------------------------------------
# KPIs – arranged in a 2×2 grid with colour accents
# ---------------------------------------------------------------------------
revenue_total = filtered["Revenue"].sum()
transaction_count = len(filtered)
units_sold = filtered["Quantity"].sum()
avg_transaction = revenue_total / transaction_count if transaction_count else 0

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric(label="💰 Total Revenue", value=f"₦{revenue_total:,.2f}", delta=None)
with c2:
    st.metric(label="📊 Transactions", value=f"{transaction_count:,}")
with c3:
    st.metric(label="📦 Units Sold", value=f"{units_sold:,}")
with c4:
    st.metric(label="🧾 Avg. Transaction", value=f"₦{avg_transaction:,.2f}")

st.divider()

# ---------------------------------------------------------------------------
# Visualisation sections – using tabs for a clean layout
# ---------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["Regional Revenue", "Product Mix", "Monthly Trend"])

with tab1:
    region_df = (
        filtered.groupby("Region", as_index=False)["Revenue"].sum()
    )
    fig_region = px.bar(
        region_df,
        x="Region",
        y="Revenue",
        title="Revenue by Region",
        text_auto="{:.2s}",
        color="Region",
        template="plotly_white",
    )
    st.plotly_chart(fig_region, use_container_width=True)

with tab2:
    product_df = (
        filtered.groupby("Product", as_index=False)["Revenue"].sum()
        .sort_values("Revenue", ascending=False)
    )
    fig_product = px.pie(
        product_df,
        names="Product",
        values="Revenue",
        title="Revenue Share by Product",
        hole=0.4,
        template="plotly_white",
    )
    st.plotly_chart(fig_product, use_container_width=True)

with tab3:
    monthly_df = filtered.copy()
    monthly_df["Month"] = monthly_df["Date"].dt.to_period("M").astype(str)
    month_rev = (
        monthly_df.groupby("Month", as_index=False)["Revenue"].sum()
        .sort_values("Month")
    )
    fig_month = px.line(
        month_rev,
        x="Month",
        y="Revenue",
        title="Monthly Revenue Trend",
        markers=True,
        template="plotly_white",
    )
    st.plotly_chart(fig_month, use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# Detailed transaction table
# ---------------------------------------------------------------------------
st.subheader("Sales Transactions")
st.dataframe(
    filtered.sort_values("Date", ascending=False),
    use_container_width=True,
    hide_index=True,
)

# ---------------------------------------------------------------------------
# Downloadable report
# ---------------------------------------------------------------------------
csv_bytes = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Filtered Report",
    data=csv_bytes,
    file_name="sales_report.csv",
    mime="text/csv",
    key="download-btn",
)
