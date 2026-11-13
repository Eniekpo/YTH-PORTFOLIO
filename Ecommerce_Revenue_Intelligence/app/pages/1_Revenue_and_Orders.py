import streamlit as st,plotly.express as px
from app.shared import get_data,filter_data
from src.analytics import monthly_kpis,country_performance
st.set_page_config(page_title='Revenue & Orders',layout='wide'); st.title('Revenue & Orders')
s,a=get_data()
if s is None:st.info('Upload or download the UCI workbook.');st.stop()
s=filter_data(s); m=monthly_kpis(s)
a,b=st.columns(2)
a.plotly_chart(px.line(m,x='month',y='revenue',markers=True,title='Revenue by month'),use_container_width=True); b.plotly_chart(px.bar(m,x='month',y='orders',title='Distinct orders by month'),use_container_width=True)
c,d=st.columns(2); c.plotly_chart(px.line(m,x='month',y='aov',markers=True,title='Average order value'),use_container_width=True); co=country_performance(s).head(15).sort_values('revenue'); d.plotly_chart(px.bar(co,x='revenue',y='country',orientation='h',title='Revenue by country'),use_container_width=True)
st.dataframe(m,use_container_width=True,hide_index=True)
