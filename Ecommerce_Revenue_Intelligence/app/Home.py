import streamlit as st
import plotly.express as px

from shared import get_data, filter_data
from src.analytics import headline, monthly_kpis, country_performance

st.set_page_config(page_title='E-commerce Revenue Intelligence', layout='wide')
st.markdown(
    '<style>.block-container{padding-top:1.2rem} [data-testid=stMetric]{background:#f1f5f9;padding:14px;border-radius:10px} h1,h2{color:#102a43}</style>',
    unsafe_allow_html=True,
)
st.title('E-commerce Revenue Intelligence')
st.caption('Executive overview | Online Retail II | GBP')

s, audit = get_data()
if s is None:
    st.info('Download the source with `python download_data.py` or upload the UCI workbook in the sidebar.')
    st.stop()

s = filter_data(s)
if s.empty:
    st.warning('No rows match the selected filters.')
    st.stop()

m = headline(s)
cols = st.columns(5)
metric_values = [
    f"£{m['revenue']:,.0f}",
    f"{m['orders']:,}",
    f"{m['customers']:,}",
    f"£{m['aov']:,.2f}",
    f"{m['units']:,.0f}",
]
for c, label, val in zip(cols, ['Revenue', 'Orders', 'Identified customers', 'Average order value', 'Units sold'], metric_values):
    c.metric(label, val)

left, right = st.columns([1.4, 1])
mon = monthly_kpis(s)
co = country_performance(s).head(10).sort_values('revenue')
with left:
    st.subheader('Monthly revenue')
    st.plotly_chart(px.area(mon, x='month', y='revenue', markers=True, color_discrete_sequence=['#2563eb']), use_container_width=True)
with right:
    st.subheader('Top countries')
    st.plotly_chart(px.bar(co, x='revenue', y='country', orientation='h', color_discrete_sequence=['#0f766e']), use_container_width=True)

st.subheader('Monthly KPI detail')
st.dataframe(mon, use_container_width=True, hide_index=True)
st.caption('Revenue includes valid positive sales lines. This dataset has no product cost, so profit and margin are not calculated.')
