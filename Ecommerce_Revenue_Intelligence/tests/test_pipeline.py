import pandas as pd
from src.cleaning import clean_transactions
from src.analytics import monthly_kpis,build_rfm,headline
def data():return pd.DataFrame({'invoice_no':['100','100','101','C102','103'],'stock_code':['A','B','A','A','C'],'description':['A','B','A','A','C'],'quantity':[2,1,3,-1,1],'invoice_date':pd.to_datetime(['2011-01-01','2011-01-01','2011-02-01','2011-02-02','2011-03-01']),'unit_price':[10,5,10,10,0],'customer_id':[1,1,2,1,None],'country':['UK','UK','FR','UK','UK']})
def test_sales_cleaning():
 s,a=clean_transactions(data());assert len(s)==3 and a['cancellation_rows']==1 and a['negative_quantity_rows']==1
def test_monthly_metrics():
 s,_=clean_transactions(data());m=monthly_kpis(s);assert m.orders.sum()==2 and m.iloc[0].aov==25
def test_rfm_known_customers_only():
 s,_=clean_transactions(data());r=build_rfm(s);assert set(r.customer_id.astype(int))=={1,2}
def test_headline_revenue():
 s,_=clean_transactions(data());assert headline(s)['revenue']==55
