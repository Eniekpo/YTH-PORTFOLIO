import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from src.data import load_retail_file
from src.cleaning import clean_transactions

DATA_DIR = PROJECT_ROOT / 'data'


@st.cache_data(show_spinner='Loading and cleaning transactions...')
def load_local():
    raw_path = DATA_DIR / 'raw' / 'online_retail_II.xlsx'
    return clean_transactions(load_retail_file(raw_path))


def get_data():
    f = st.sidebar.file_uploader('Upload UCI workbook or CSV', type=['xlsx', 'xls', 'csv'])
    if f:
        processed_dir = DATA_DIR / 'processed'
        processed_dir.mkdir(parents=True, exist_ok=True)
        uploaded_path = processed_dir / ('dashboard_upload' + Path(f.name).suffix)
        uploaded_path.write_bytes(f.getvalue())
        return clean_transactions(load_retail_file(uploaded_path))

    raw_path = DATA_DIR / 'raw' / 'online_retail_II.xlsx'
    if raw_path.exists():
        return load_local()
    return None, None


def filter_data(s):
    if s is None or s.empty:
        return s

    st.sidebar.markdown('### Filters')
    years = sorted(s.year.dropna().unique())
    ys = st.sidebar.multiselect('Year', years, default=years)
    countries = sorted(s.country.dropna().unique())
    cs = st.sidebar.multiselect('Country', countries, default=countries)
    return s[s.year.isin(ys) & s.country.isin(cs)]
