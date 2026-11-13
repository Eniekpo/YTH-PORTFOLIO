import pandas as pd
def monthly_kpis(s):
 x=s.groupby('month',as_index=False).agg(revenue=('line_revenue','sum'),orders=('invoice_no','nunique'),units=('quantity','sum')); x['aov']=x.revenue/x.orders.replace(0,float('nan')); return x.sort_values('month')
def product_performance(s):
 return s.groupby(['stock_code','description'],dropna=False,as_index=False).agg(revenue=('line_revenue','sum'),units=('quantity','sum'),orders=('invoice_no','nunique')).sort_values('revenue',ascending=False)
def country_performance(s):
 return s.groupby('country',dropna=False,as_index=False).agg(revenue=('line_revenue','sum'),orders=('invoice_no','nunique'),customers=('customer_id','nunique'),units=('quantity','sum')).sort_values('revenue',ascending=False)
def segment(r):
 R,F,M=int(r.r_score),int(r.f_score),int(r.m_score)
 if R>=4 and F>=4 and M>=4:return 'Champions'
 if R>=3 and F>=3:return 'Loyal Customers'
 if R>=4 and F<=2:return 'Recent Customers'
 if R>=3 and F<=2:return 'Promising'
 if R<=2 and F>=3:return 'At Risk'
 if R==1 and F<=2:return 'Lost Customers'
 return 'Needs Attention'
def build_rfm(s):
 d=s.dropna(subset=['customer_id']).copy()
 if d.empty:return pd.DataFrame()
 snap=d.invoice_date.max()+pd.Timedelta(days=1)
 r=d.groupby('customer_id').agg(last_purchase=('invoice_date','max'),first_purchase=('invoice_date','min'),frequency=('invoice_no','nunique'),monetary=('line_revenue','sum'),country=('country',lambda x:x.mode().iat[0] if not x.mode().empty else 'Unknown')).reset_index()
 r['recency_days']=(snap-r.last_purchase).dt.days; r['tenure_days']=(r.last_purchase-r.first_purchase).dt.days
 r['r_score']=pd.qcut(r.recency_days.rank(method='first'),5,labels=[5,4,3,2,1]).astype(int); r['f_score']=pd.qcut(r.frequency.rank(method='first'),5,labels=[1,2,3,4,5]).astype(int); r['m_score']=pd.qcut(r.monetary.rank(method='first'),5,labels=[1,2,3,4,5]).astype(int)
 r['rfm_score']=r.r_score.astype(str)+r.f_score.astype(str)+r.m_score.astype(str); r['segment']=r.apply(segment,axis=1); return r.sort_values('monetary',ascending=False)
def headline(s):
 rev=float(s.line_revenue.sum()); orders=int(s.invoice_no.nunique()); return {'revenue':rev,'orders':orders,'customers':int(s.customer_id.nunique()),'aov':rev/orders if orders else 0,'units':float(s.quantity.sum())}
