import streamlit as st,pandas as pd
from app.shared import get_data
st.set_page_config(page_title='Data Quality',layout='wide');st.title('Data Quality & Transaction Audit')
s,a=get_data()
if s is None:st.info('Upload or download the UCI workbook.');st.stop()
cols=st.columns(4)
for c,k in zip(cols,['source_rows','positive_sales_rows','cancellation_rows','missing_customer_rows']):c.metric(k.replace('_',' ').title(),f'{a[k]:,}')
st.subheader('Audit metrics');st.json(a)
fields=['invoice_no','stock_code','description','quantity','invoice_date','unit_price','customer_id','country']; q=pd.DataFrame({'field':fields,'missing_count':[int(s[f].isna().sum()) for f in fields]});q['missing_pct']=100*q.missing_count/max(1,len(s));st.dataframe(q,use_container_width=True,hide_index=True)
st.caption('Missing customer IDs are retained for aggregate revenue but excluded from customer-level RFM. Cancellation and negative-quantity rows are excluded from positive-sales KPIs.')
