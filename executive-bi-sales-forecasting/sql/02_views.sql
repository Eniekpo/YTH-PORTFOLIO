DROP VIEW IF EXISTS vw_sales_enriched;
CREATE VIEW vw_sales_enriched AS
SELECT
    s.sales_line_id,
    s.order_id,
    s.order_date,
    CAST(strftime('%Y', s.order_date) AS INTEGER) AS sales_year,
    CAST(strftime('%m', s.order_date) AS INTEGER) AS sales_month,
    c.customer_id,
    c.customer_name,
    c.region,
    c.country,
    c.customer_type,
    p.product_id,
    p.product_name,
    p.category,
    s.channel,
    s.quantity,
    s.unit_price,
    s.discount_pct,
    s.gross_sales,
    s.discount_amount,
    s.return_amount,
    s.net_sales,
    s.cost,
    s.gross_profit,
    CASE WHEN s.net_sales = 0 THEN 0 ELSE s.gross_profit / s.net_sales END AS gross_margin,
    s.returned
FROM fact_sales s
JOIN dim_customer c ON c.customer_id = s.customer_id
JOIN dim_product p ON p.product_id = s.product_id;

DROP VIEW IF EXISTS vw_monthly_kpis;
CREATE VIEW vw_monthly_kpis AS
SELECT
    substr(order_date, 1, 7) || '-01' AS month,
    SUM(net_sales) AS revenue,
    SUM(gross_profit) AS gross_profit,
    COUNT(DISTINCT order_id) AS orders,
    COUNT(DISTINCT customer_id) AS customers,
    SUM(quantity) AS units,
    SUM(return_amount) AS returns
FROM fact_sales
GROUP BY substr(order_date, 1, 7);
