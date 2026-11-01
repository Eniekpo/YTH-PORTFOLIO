from pathlib import Path
import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "powerbi" / "retail_sales_powerbi.csv"
DB = ROOT / "sql" / "analytics_lab.db"

st.set_page_config(page_title="AnalyticsPath Learning Lab", page_icon="📊", layout="wide")
st.title("AnalyticsPath Learning Lab")
st.caption("Excel → SQL → Python → Power BI")

df = pd.read_csv(DATA, parse_dates=["Order_Date"])

modules = {
    "Overview": "Understand the business scenario, dataset grain, learning path, and portfolio outcome.",
    "Excel": "Use formulas, aggregation, and charts to move from raw transactions to an executive dashboard.",
    "SQL": "Query, group, filter, rank, and compare commercial performance using SQLite.",
    "Python": "Build a reproducible analytical workflow with quality checks, summaries, and visualizations.",
    "Power BI": "Build an interactive management report with reusable DAX measures and time intelligence.",
    "Capstone": "Reconcile results across tools and communicate evidence-based management recommendations.",
}

module = st.sidebar.radio("Learning module", list(modules))
st.sidebar.markdown("---")
st.sidebar.write("**Dataset:** 1,800 synthetic orders")
st.sidebar.write("**Period:** 2024–2025")
st.sidebar.caption("Training data only.")

st.subheader(module)
st.info(modules[module])

if module == "Overview":
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", f"{len(df):,}")
    c2.metric("Revenue", f"${df['Revenue'].sum():,.0f}")
    c3.metric("Profit", f"${df['Profit'].sum():,.0f}")
    c4.metric("Orders", f"{df['Order_ID'].nunique():,}")
    st.markdown("### Dataset preview")
    st.dataframe(df.head(20), use_container_width=True, hide_index=True)
    st.markdown("""
### Learning path
1. **Excel:** formulas and dashboard fundamentals
2. **SQL:** querying and aggregation
3. **Python:** reproducible analysis and visualization
4. **Power BI:** interactive reporting and DAX
5. **Capstone:** reconcile and communicate
""")

elif module == "Excel":
    st.markdown("""
### Your tasks
- calculate Revenue, Cost, Profit, and Profit Margin;
- derive Year, Month, and Year-Month;
- create executive KPIs;
- compare regions and categories;
- create a monthly trend;
- write three evidence-based recommendations.

Open `excel/AnalyticsPath_Excel_Lab.xlsx`.
""")
    st.success("Complete Excel_Exercises before opening Excel_Solutions.")

elif module == "SQL":
    st.markdown("### Live SQL preview")
    query = st.text_area(
        "Try a SELECT query",
        "SELECT region, ROUND(SUM(revenue), 2) AS revenue\nFROM sales\nGROUP BY region\nORDER BY revenue DESC;"
    )
    if st.button("Run query"):
        normalized = query.strip().lower()
        if not normalized.startswith("select") and not normalized.startswith("with"):
            st.error("For the learning portal, use SELECT or WITH queries only.")
        else:
            try:
                con = sqlite3.connect(DB)
                result = pd.read_sql_query(query, con)
                con.close()
                st.dataframe(result, use_container_width=True, hide_index=True)
            except Exception as exc:
                st.error(str(exc))
    st.caption("Use the supplied SQL files for the complete exercise sequence.")

elif module == "Python":
    st.markdown("""
Open `python/01_python_analytics_starter.ipynb` in Jupyter.

Use `python/02_python_analytics_solution.ipynb` only after attempting the exercises.
""")
    monthly = df.groupby("Year_Month", as_index=False)["Revenue"].sum()
    st.plotly_chart(
        px.line(monthly, x="Year_Month", y="Revenue", markers=True, title="Example Analytical Output"),
        use_container_width=True
    )

elif module == "Power BI":
    st.markdown("""
Import `data/powerbi/retail_sales_powerbi.csv` into Power BI Desktop.

Then follow:
- `powerbi/POWER_BI_BUILD_GUIDE.md`
- `powerbi/DAX_MEASURES.md`
- `powerbi/MODEL_AND_WIREFRAME.md`
""")
    st.dataframe(pd.DataFrame({
        "KPI": ["Total Revenue","Total Profit","Profit Margin","Orders","Units Sold","Average Order Value"],
        "Definition": [
            "SUM(Revenue)","SUM(Profit)","Total Profit / Total Revenue",
            "Distinct Order_ID","SUM(Quantity)","Total Revenue / Orders"
        ]
    }), use_container_width=True, hide_index=True)

elif module == "Capstone":
    st.markdown("""
### Final assignment
Produce an executive retail performance review using all four tools.

Required:
- reconcile headline KPIs;
- identify regional/category/channel patterns;
- create effective visualizations;
- provide recommendations;
- state limitations.

See `assessments/CAPSTONE_BRIEF.md` and `assessments/CAPSTONE_RUBRIC.md`.
""")
    st.markdown("### Knowledge check")
    q1 = st.radio(
        "If higher discounts are associated with lower margins, what can you conclude?",
        [
            "Discounts definitely caused the lower margins",
            "There is an association, but other factors may contribute",
            "Profit margin cannot be analysed by discount"
        ],
        index=None
    )
    q2 = st.radio(
        "Why reconcile KPIs across Excel, SQL, Python and Power BI?",
        [
            "To verify definitions and transformations are consistent",
            "Because every tool should use different numbers",
            "Only to make the portfolio longer"
        ],
        index=None
    )
    if st.button("Check answers"):
        score = int(q1 == "There is an association, but other factors may contribute")
        score += int(q2 == "To verify definitions and transformations are consistent")
        st.write(f"Score: **{score}/2**")
        if score == 2:
            st.success("Correct. You are applying analytical caution and reconciliation discipline.")
