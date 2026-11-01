from __future__ import annotations

import sqlite3
from pathlib import Path
import pandas as pd

from .config import DB_PATH, RAW_DIR, ROOT_DIR


def _execute_sql_file(conn: sqlite3.Connection, path: Path) -> None:
    conn.executescript(path.read_text(encoding="utf-8"))


def build_database(raw_dir: Path = RAW_DIR, db_path: Path = DB_PATH) -> Path:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    customers = pd.read_csv(raw_dir / "customers.csv")
    products = pd.read_csv(raw_dir / "products.csv")
    sales = pd.read_csv(raw_dir / "sales.csv")

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        _execute_sql_file(conn, ROOT_DIR / "sql" / "01_schema.sql")
        customers.to_sql("dim_customer", conn, if_exists="append", index=False)
        products.to_sql("dim_product", conn, if_exists="append", index=False)
        sales.to_sql("fact_sales", conn, if_exists="append", index=False)
        _execute_sql_file(conn, ROOT_DIR / "sql" / "02_views.sql")
        conn.commit()
    finally:
        conn.close()
    return db_path


def query_df(query: str, params: tuple | dict | None = None, db_path: Path = DB_PATH) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    try:
        return pd.read_sql_query(query, conn, params=params)
    finally:
        conn.close()
