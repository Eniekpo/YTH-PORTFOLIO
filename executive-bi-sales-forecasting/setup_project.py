from pathlib import Path

from src.config import DB_PATH, RAW_DIR
from src.data_generator import generate_sales_data
from src.database import build_database


def main() -> None:
    required = [RAW_DIR / "customers.csv", RAW_DIR / "products.csv", RAW_DIR / "sales.csv"]
    if not all(path.exists() for path in required):
        print("Generating synthetic portfolio dataset...")
        customers, products, sales = generate_sales_data()
        print(f"  Customers: {len(customers):,}")
        print(f"  Products:  {len(products):,}")
        print(f"  Sales rows:{len(sales):,}")
    else:
        print("Raw CSV files already exist. Skipping generation.")

    print("Building SQLite analytical database...")
    db_path = build_database()
    print(f"Database ready: {db_path}")
    print("\nSetup complete. Run: streamlit run app.py")


if __name__ == "__main__":
    main()
