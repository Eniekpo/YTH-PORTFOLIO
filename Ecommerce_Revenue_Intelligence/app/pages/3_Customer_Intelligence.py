import streamlit as st,plotly.express as px
from shared import get_data,filter_data
from src.analytics import build_rfm
st.set_page_config(page_title='Customer Intelligence',layout='wide');st.title('Customer Intelligence');st.caption('RFM: recency, distinct invoice frequency and monetary value')
s,a=get_data()
if s is None:st.info('Upload or download the UCI workbook.');st.stop()
r=build_rfm(filter_data(s))
if r.empty:st.warning('No identified customers available.');st.stop()
a,b,c=st.columns(3);a.metric('Customers scored',f'{len(r):,}');b.metric('Average recency',f'{r.recency_days.mean():.0f} days');c.metric('Average customer revenue',f"£{r.monetary.mean():,.2f}")
seg=r.groupby('segment',as_index=False).agg(customers=('customer_id','count'),revenue=('monetary','sum'));x,y=st.columns(2);x.plotly_chart(px.treemap(seg,path=['segment'],values='customers',color='revenue',title='Customer segment mix'),use_container_width=True);y.plotly_chart(px.bar(seg.sort_values('revenue'),x='revenue',y='segment',orientation='h',title='Revenue by segment'),use_container_width=True)
for col,field,title in zip(st.columns(3),['r_score','f_score','m_score'],['Recency score','Frequency score','Monetary score']):col.plotly_chart(px.histogram(r,x=field,nbins=5,title=title),use_container_width=True)
st.dataframe(r,use_container_width=True,hide_index=True);st.download_button('Download RFM CSV',r.to_csv(index=False).encode(),'customer_rfm.csv')
