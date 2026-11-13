import streamlit as st,plotly.express as px
from app.shared import get_data,filter_data
from src.analytics import product_performance
st.set_page_config(page_title='Product Intelligence',layout='wide');st.title('Product Intelligence')
s,a=get_data()
if s is None:st.info('Upload or download the UCI workbook.');st.stop()
p=product_performance(filter_data(s)); n=st.slider('Number of products',5,30,15); top=p.head(n).sort_values('revenue')
st.plotly_chart(px.bar(top,x='revenue',y='description',orientation='h',hover_data=['stock_code','units','orders'],title='Top products by revenue'),use_container_width=True)
p['revenue_share_pct']=100*p.revenue/p.revenue.sum();p['cumulative_share_pct']=p.revenue_share_pct.cumsum();st.plotly_chart(px.line(p.head(100),y='cumulative_share_pct',title='Revenue concentration across top 100 products'),use_container_width=True)
st.dataframe(p,use_container_width=True,hide_index=True);st.download_button('Download product CSV',p.to_csv(index=False).encode(),'product_performance.csv')
