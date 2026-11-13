from pathlib import Path
import streamlit as st
from src.data import load_retail_file
from src.cleaning import clean_transactions
@st.cache_data(show_spinner='Loading and cleaning transactions...')
def load_local(): return clean_transactions(load_retail_file('data/raw/online_retail_II.xlsx'))
def get_data():
 f=st.sidebar.file_uploader('Upload UCI workbook or CSV',type=['xlsx','xls','csv'])
 if f:
  p=Path('data/processed')/('dashboard_upload'+Path(f.name).suffix); p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(f.getvalue()); return clean_transactions(load_retail_file(p))
 if Path('data/raw/online_retail_II.xlsx').exists():return load_local()
 return None,None
def filter_data(s):
 st.sidebar.markdown('### Filters'); years=sorted(s.year.dropna().unique()); ys=st.sidebar.multiselect('Year',years,default=years); countries=sorted(s.country.dropna().unique()); cs=st.sidebar.multiselect('Country',countries,default=countries); return s[s.year.isin(ys)&s.country.isin(cs)]
