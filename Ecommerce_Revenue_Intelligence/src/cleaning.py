import pandas as pd
def clean_transactions(raw):
 d=raw.copy()
 for c in ['invoice_no','stock_code','description','country']: d[c]=d[c].astype('string').str.strip()
 d['quantity']=pd.to_numeric(d.quantity,errors='coerce'); d['unit_price']=pd.to_numeric(d.unit_price,errors='coerce'); d['invoice_date']=pd.to_datetime(d.invoice_date,errors='coerce'); d['customer_id']=pd.to_numeric(d.customer_id,errors='coerce').astype('Int64')
 d['is_cancellation']=d.invoice_no.str.upper().str.startswith('C',na=False); d['line_revenue']=d.quantity*d.unit_price
 d['is_positive_sale']=(~d.is_cancellation)&d.quantity.gt(0)&d.unit_price.gt(0)&d.invoice_date.notna()
 d['year']=d.invoice_date.dt.year; d['month']=d.invoice_date.dt.to_period('M').astype('string'); d['weekday']=d.invoice_date.dt.day_name(); d['hour']=d.invoice_date.dt.hour
 audit={'source_rows':len(d),'positive_sales_rows':int(d.is_positive_sale.sum()),'cancellation_rows':int(d.is_cancellation.sum()),'negative_quantity_rows':int(d.quantity.lt(0).sum()),'missing_customer_rows':int(d.customer_id.isna().sum()),'invalid_date_rows':int(d.invoice_date.isna().sum()),'invalid_price_rows':int((d.unit_price.isna()|(d.unit_price<=0)).sum()),'duplicate_rows':int(d.duplicated().sum()),'date_min':str(d.invoice_date.min()),'date_max':str(d.invoice_date.max())}
 return d.loc[d.is_positive_sale].copy(),audit
