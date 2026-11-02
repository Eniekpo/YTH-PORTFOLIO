#!/usr/bin/env bash
set -e
python -m app.seed
streamlit run app/dashboard.py
