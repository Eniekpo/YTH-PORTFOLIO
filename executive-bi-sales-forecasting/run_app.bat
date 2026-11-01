@echo off
python setup_project.py
if errorlevel 1 exit /b 1
streamlit run app.py
