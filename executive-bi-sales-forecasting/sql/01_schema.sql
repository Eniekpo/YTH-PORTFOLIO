DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS dim_customer;
DROP TABLE IF EXISTS dim_product;

CREATE TABLE dim_customer (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL,
    region TEXT NOT NULL,
    country TEXT NOT NULL,
    customer_type TEXT NOT NULL,
    signup_date TEXT NOT NULL
);

CREATE TABLE dim_product (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    list_price REAL NOT NULL,
    unit_cost REAL NOT NULL
);

CREATE TABLE fact_sales (
    sales_line_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT NOT NULL,
    order_date TEXT NOT NULL,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    channel TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    discount_pct REAL NOT NULL,
    gross_sales REAL NOT NULL,
    discount_amount REAL NOT NULL,
    return_amount REAL NOT NULL,
    net_sales REAL NOT NULL,
    cost REAL NOT NULL,
    gross_profit REAL NOT NULL,
    returned INTEGER NOT NULL,
    FOREIGN KEY(customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY(product_id) REFERENCES dim_product(product_id)
);

CREATE INDEX idx_sales_order_date ON fact_sales(order_date);
CREATE INDEX idx_sales_customer ON fact_sales(customer_id);
CREATE INDEX idx_sales_product ON fact_sales(product_id);
CREATE INDEX idx_sales_channel ON fact_sales(channel);
