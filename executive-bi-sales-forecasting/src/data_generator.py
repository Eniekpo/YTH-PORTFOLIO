from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd

from .config import RAW_DIR


REGION_COUNTRIES = {
    "North America": ["United States", "Canada"],
    "Europe": ["United Kingdom", "Germany", "France"],
    "West Africa": ["Nigeria", "Ghana"],
    "East Africa": ["Kenya", "Uganda"],
}

CATEGORY_PRODUCTS = {
    "Electronics": [
        ("Wireless Keyboard", 45, 24), ("Noise-Canceling Headphones", 120, 72),
        ("USB-C Dock", 95, 56), ("Portable SSD 1TB", 130, 82),
        ("27-inch Monitor", 240, 162), ("Webcam Pro", 85, 48),
        ("Mechanical Keyboard", 110, 66), ("Bluetooth Speaker", 90, 52),
    ],
    "Office Supplies": [
        ("Premium Notebook Set", 18, 7), ("Ergonomic Mouse Pad", 25, 10),
        ("Desk Organizer", 32, 14), ("Printer Paper Case", 44, 25),
        ("Gel Pen Pack", 12, 4), ("Whiteboard Kit", 38, 17),
        ("Document Folder Set", 20, 8), ("Desk Lamp", 48, 23),
    ],
    "Furniture": [
        ("Ergonomic Office Chair", 310, 190), ("Standing Desk", 460, 300),
        ("Bookshelf", 180, 105), ("Mobile Pedestal", 150, 82),
        ("Conference Chair", 220, 130), ("Compact Work Desk", 280, 165),
        ("Monitor Riser", 70, 33), ("Foot Rest", 55, 24),
    ],
    "Home & Kitchen": [
        ("Air Fryer", 145, 88), ("Electric Kettle", 60, 31),
        ("Blender", 95, 52), ("Coffee Maker", 115, 67),
        ("Storage Container Set", 38, 16), ("Digital Kitchen Scale", 36, 15),
        ("Cookware Set", 180, 112), ("Water Filter Jug", 48, 21),
    ],
    "Accessories": [
        ("Laptop Sleeve", 35, 13), ("Travel Backpack", 78, 35),
        ("Cable Organizer", 18, 6), ("Phone Stand", 22, 7),
        ("Power Bank", 58, 31), ("Reusable Bottle", 28, 10),
        ("Travel Adapter", 42, 19), ("Tech Pouch", 34, 14),
    ],
}

CHANNELS = ["Online Store", "Marketplace", "Retail", "B2B"]
CHANNEL_WEIGHTS = [0.46, 0.22, 0.18, 0.14]


def _product_table() -> pd.DataFrame:
    rows = []
    product_id = 1001
    for category, products in CATEGORY_PRODUCTS.items():
        for product_name, list_price, unit_cost in products:
            rows.append({
                "product_id": product_id,
                "product_name": product_name,
                "category": category,
                "list_price": float(list_price),
                "unit_cost": float(unit_cost),
            })
            product_id += 1
    return pd.DataFrame(rows)


def _customer_table(rng: np.random.Generator, n_customers: int) -> pd.DataFrame:
    regions = np.array(list(REGION_COUNTRIES.keys()))
    region_probs = np.array([0.36, 0.28, 0.24, 0.12])
    selected_regions = rng.choice(regions, n_customers, p=region_probs)

    first_names = ["Amina", "Daniel", "Grace", "Samuel", "Maya", "Noah", "Zainab", "Liam", "Chidi", "Olivia", "Kwame", "Sophia", "Tunde", "Emma", "David", "Fatima"]
    last_names = ["Okafor", "Smith", "Mensah", "Brown", "Adebayo", "Johnson", "Muller", "Wilson", "Njoroge", "Taylor", "Bello", "Martin", "Clark", "Khan", "Walker", "Ali"]
    segments = rng.choice(["Consumer", "SMB", "Enterprise"], n_customers, p=[0.67, 0.25, 0.08])
    signup_dates = pd.to_datetime(rng.choice(pd.date_range("2022-01-01", "2026-06-30", freq="D"), n_customers))

    rows = []
    for i, region in enumerate(selected_regions, start=1):
        country = rng.choice(REGION_COUNTRIES[region])
        rows.append({
            "customer_id": 50000 + i,
            "customer_name": f"{rng.choice(first_names)} {rng.choice(last_names)}",
            "region": region,
            "country": country,
            "customer_type": segments[i - 1],
            "signup_date": signup_dates[i - 1].date().isoformat(),
        })
    return pd.DataFrame(rows)


def generate_sales_data(
    output_dir: Path = RAW_DIR,
    seed: int = 42,
    n_customers: int = 2500,
    n_orders: int = 30000,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Generate realistic synthetic customers, products, and sales line items."""
    output_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)

    products = _product_table()
    customers = _customer_table(rng, n_customers)

    start = pd.Timestamp("2023-01-01")
    end = pd.Timestamp("2026-10-31")
    dates = pd.date_range(start, end, freq="D")

    day_index = np.arange(len(dates))
    trend = 0.78 + 0.52 * (day_index / max(1, day_index.max()))
    annual = 1 + 0.14 * np.sin(2 * np.pi * day_index / 365.25 - 1.1)
    weekday = np.where(dates.dayofweek < 5, 1.08, 0.80)
    holiday = np.where(dates.month.isin([11, 12]), 1.30, 1.0)
    weights = trend * annual * weekday * holiday
    weights = weights / weights.sum()
    order_dates = pd.to_datetime(rng.choice(dates, n_orders, p=weights)).sort_values()

    customer_ids = customers["customer_id"].to_numpy()
    customer_types = customers.set_index("customer_id")["customer_type"]
    product_ids = products["product_id"].to_numpy()
    price_map = products.set_index("product_id")["list_price"].to_dict()
    cost_map = products.set_index("product_id")["unit_cost"].to_dict()

    line_rows = []
    order_num = 1
    for order_date in order_dates:
        customer_id = int(rng.choice(customer_ids))
        ctype = customer_types.loc[customer_id]
        line_count = int(rng.choice([1, 2, 3, 4], p=[0.60, 0.25, 0.11, 0.04]))
        selected_products = rng.choice(product_ids, size=line_count, replace=False)
        channel = rng.choice(CHANNELS, p=CHANNEL_WEIGHTS)
        order_id = f"ORD-{order_num:06d}"
        order_num += 1

        for product_id in selected_products:
            if ctype == "Enterprise":
                qty = int(rng.choice([2, 3, 4, 5, 6], p=[0.18, 0.24, 0.24, 0.20, 0.14]))
                base_discount = 0.08
            elif ctype == "SMB":
                qty = int(rng.choice([1, 2, 3, 4], p=[0.40, 0.34, 0.18, 0.08]))
                base_discount = 0.04
            else:
                qty = int(rng.choice([1, 2, 3], p=[0.77, 0.19, 0.04]))
                base_discount = 0.015

            promo = 0.04 if order_date.month in [11, 12] else 0.0
            random_discount = float(rng.choice([0, 0.02, 0.05, 0.10], p=[0.56, 0.22, 0.16, 0.06]))
            discount_pct = min(0.22, base_discount + promo + random_discount)

            list_price = price_map[int(product_id)]
            # Gentle price inflation over time.
            years_from_start = (order_date - start).days / 365.25
            unit_price = list_price * (1 + 0.035 * years_from_start) * rng.normal(1.0, 0.025)
            unit_price = max(1.0, round(unit_price, 2))
            gross_sales = qty * unit_price
            discount_amount = gross_sales * discount_pct
            net_sales = gross_sales - discount_amount
            cost = qty * cost_map[int(product_id)] * (1 + 0.020 * years_from_start)
            gross_profit = net_sales - cost

            returned = rng.random() < (0.025 if channel == "Online Store" else 0.015)
            return_amount = round(net_sales * rng.uniform(0.40, 1.0), 2) if returned else 0.0
            net_sales_after_returns = net_sales - return_amount
            gross_profit_after_returns = gross_profit - return_amount

            line_rows.append({
                "order_id": order_id,
                "order_date": order_date.date().isoformat(),
                "customer_id": customer_id,
                "product_id": int(product_id),
                "channel": channel,
                "quantity": qty,
                "unit_price": round(unit_price, 2),
                "discount_pct": round(discount_pct, 4),
                "gross_sales": round(gross_sales, 2),
                "discount_amount": round(discount_amount, 2),
                "return_amount": round(return_amount, 2),
                "net_sales": round(net_sales_after_returns, 2),
                "cost": round(cost, 2),
                "gross_profit": round(gross_profit_after_returns, 2),
                "returned": int(returned),
            })

    sales = pd.DataFrame(line_rows)

    customers.to_csv(output_dir / "customers.csv", index=False)
    products.to_csv(output_dir / "products.csv", index=False)
    sales.to_csv(output_dir / "sales.csv", index=False)

    return customers, products, sales


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic data for the Executive BI project.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--customers", type=int, default=2500)
    parser.add_argument("--orders", type=int, default=30000)
    args = parser.parse_args()

    customers, products, sales = generate_sales_data(
        seed=args.seed,
        n_customers=args.customers,
        n_orders=args.orders,
    )
    print(f"Generated {len(customers):,} customers, {len(products):,} products, and {len(sales):,} sales lines.")


if __name__ == "__main__":
    main()
