from pathlib import Path
import json
from src.data import load_retail_file
from src.cleaning import clean_transactions
from src.analytics import monthly_kpis,product_performance,country_performance,build_rfm
def run_pipeline(input_path,output_dir):
 out=Path(output_dir); out.mkdir(parents=True,exist_ok=True); raw=load_retail_file(input_path); sales,audit=clean_transactions(raw)
 result={'clean_sales':out/'clean_sales.parquet','monthly_kpis':out/'monthly_kpis.csv','product_performance':out/'product_performance.csv','country_performance':out/'country_performance.csv','customer_rfm':out/'customer_rfm.csv','data_quality':out/'data_quality.json'}
 sales.to_parquet(result['clean_sales'],index=False); monthly_kpis(sales).to_csv(result['monthly_kpis'],index=False); product_performance(sales).to_csv(result['product_performance'],index=False); country_performance(sales).to_csv(result['country_performance'],index=False); build_rfm(sales).to_csv(result['customer_rfm'],index=False); result['data_quality'].write_text(json.dumps(audit,indent=2)); return result
