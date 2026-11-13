CREATE SCHEMA IF NOT EXISTS retail_analytics;
CREATE TABLE IF NOT EXISTS retail_analytics.customers(customer_id BIGINT PRIMARY KEY,country TEXT);
CREATE TABLE IF NOT EXISTS retail_analytics.products(stock_code TEXT PRIMARY KEY,description TEXT);
CREATE TABLE IF NOT EXISTS retail_analytics.orders(invoice_no TEXT PRIMARY KEY,invoice_date TIMESTAMP NOT NULL,customer_id BIGINT REFERENCES retail_analytics.customers(customer_id),country TEXT);
CREATE TABLE IF NOT EXISTS retail_analytics.order_items(order_item_id BIGSERIAL PRIMARY KEY,invoice_no TEXT NOT NULL REFERENCES retail_analytics.orders(invoice_no),stock_code TEXT NOT NULL REFERENCES retail_analytics.products(stock_code),quantity INTEGER NOT NULL,unit_price NUMERIC(12,2) NOT NULL,line_revenue NUMERIC(14,2) NOT NULL);
CREATE INDEX IF NOT EXISTS idx_orders_date ON retail_analytics.orders(invoice_date);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON retail_analytics.orders(customer_id);
