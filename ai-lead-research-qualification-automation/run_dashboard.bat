@echo off
python -m app.seed
streamlit run app/dashboard.py
