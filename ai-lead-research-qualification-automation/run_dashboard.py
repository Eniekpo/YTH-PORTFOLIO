#!/usr/bin/env python3
"""Convenience script to launch the Streamlit dashboard.
Run with:
    python3 run_dashboard.py
"""
import subprocess
import sys
import os

def main() -> None:
    # Ensure the project root is in PYTHONPATH so that `app` can be imported.
    project_root = os.path.abspath(os.path.dirname(__file__))
    sys.path.insert(0, project_root)
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app/dashboard.py"], check=False)

if __name__ == "__main__":
    main()

