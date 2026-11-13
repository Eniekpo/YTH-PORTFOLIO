from pathlib import Path
import pandas as pd
MAP={'Invoice':'invoice_no','InvoiceNo':'invoice_no','StockCode':'stock_code','Description':'description','Quantity':'quantity','InvoiceDate':'invoice_date','Price':'unit_price','UnitPrice':'unit_price','Customer ID':'customer_id','CustomerID':'customer_id','Country':'country'}
REQ=['invoice_no','stock_code','description','quantity','invoice_date','unit_price','customer_id','country']
def load_retail_file(path):
 p=Path(path)
 if not p.exists(): raise FileNotFoundError(f'{p} missing. Run python download_data.py or upload the workbook.')
 if p.suffix.lower() in ('.xlsx','.xls'):
  sheets=pd.read_excel(p,sheet_name=None,engine='openpyxl'); frames=[x.assign(source_sheet=str(k)) for k,x in sheets.items() if x is not None and not x.empty]; df=pd.concat(frames,ignore_index=True)
 elif p.suffix.lower()=='.csv': df=pd.read_csv(p)
 else: raise ValueError('Use xlsx, xls or csv.')
 df.columns=[str(c).strip() for c in df.columns]; df=df.rename(columns={c:MAP[c] for c in df.columns if c in MAP})
 missing=set(REQ)-set(df.columns)
 if missing: raise ValueError(f'Missing required fields: {sorted(missing)}')
 return df
