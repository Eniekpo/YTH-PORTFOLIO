import json
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
from src.data import load_retail_file
from src.cleaning import clean_transactions

DATA_DIR = PROJECT_ROOT / 'data'


@st.cache_data(show_spinner='Loading and cleaning transactions...')
def load_local():
    processed_path = DATA_DIR / 'processed' / 'clean_sales.parquet'
    audit_path = DATA_DIR / 'processed' / 'data_quality.json'
    if processed_path.exists() and audit_path.exists():
        return (
            pd.read_parquet(processed_path),
            json.loads(audit_path.read_text(encoding='utf-8')),
        )

    raw_path = DATA_DIR / 'raw' / 'online_retail_II.xlsx'
    return clean_transactions(load_retail_file(raw_path))


@st.cache_data(show_spinner='Loading and cleaning uploaded data...', max_entries=2)
def load_uploaded(file_bytes, suffix):
    with tempfile.TemporaryDirectory() as temp_dir:
        uploaded_path = Path(temp_dir) / f'upload{suffix}'
        uploaded_path.write_bytes(file_bytes)
        return clean_transactions(load_retail_file(uploaded_path))


def get_data():
    f = st.sidebar.file_uploader('Upload UCI workbook or CSV', type=['xlsx', 'xls', 'csv'])
    if f:
        return load_uploaded(f.getvalue(), Path(f.name).suffix.lower())

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
