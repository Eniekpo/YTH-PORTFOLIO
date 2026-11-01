DROP TABLE IF EXISTS sales;

CREATE TABLE sales (
    order_id TEXT PRIMARY KEY,
    order_date TEXT NOT NULL,
    region TEXT NOT NULL,
    city TEXT NOT NULL,
    category TEXT NOT NULL,
    subcategory TEXT NOT NULL,
    product TEXT NOT NULL,
    customer_segment TEXT NOT NULL,
    channel TEXT NOT NULL,
    salesperson TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    unit_cost REAL NOT NULL,
    discount REAL NOT NULL,
    revenue REAL NOT NULL,
    cost REAL NOT NULL,
    profit REAL NOT NULL,
    profit_margin REAL NOT NULL,
    year INTEGER NOT NULL,
    month TEXT NOT NULL,
    year_month TEXT NOT NULL
);
