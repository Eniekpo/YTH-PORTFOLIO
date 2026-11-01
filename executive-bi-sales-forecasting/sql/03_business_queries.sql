-- 1. Executive KPI summary
SELECT
    ROUND(SUM(net_sales), 2) AS revenue,
    ROUND(SUM(gross_profit), 2) AS gross_profit,
    ROUND(SUM(gross_profit) / NULLIF(SUM(net_sales), 0), 4) AS gross_margin,
    COUNT(DISTINCT order_id) AS orders,
    COUNT(DISTINCT customer_id) AS customers,
    ROUND(SUM(net_sales) / NULLIF(COUNT(DISTINCT order_id), 0), 2) AS average_order_value
FROM vw_sales_enriched;

-- 2. Regional performance
SELECT
    region,
    ROUND(SUM(net_sales), 2) AS revenue,
    ROUND(SUM(gross_profit), 2) AS gross_profit,
    ROUND(SUM(gross_profit) / NULLIF(SUM(net_sales), 0), 4) AS gross_margin,
    COUNT(DISTINCT order_id) AS orders
FROM vw_sales_enriched
GROUP BY region
ORDER BY revenue DESC;

-- 3. Product profitability
SELECT
    product_name,
    category,
    ROUND(SUM(net_sales), 2) AS revenue,
    ROUND(SUM(gross_profit), 2) AS gross_profit,
    ROUND(SUM(gross_profit) / NULLIF(SUM(net_sales), 0), 4) AS gross_margin,
    SUM(quantity) AS units
FROM vw_sales_enriched
GROUP BY product_name, category
ORDER BY gross_profit DESC
LIMIT 20;

-- 4. Monthly channel trend
SELECT
    substr(order_date, 1, 7) AS month,
    channel,
    ROUND(SUM(net_sales), 2) AS revenue
FROM vw_sales_enriched
GROUP BY substr(order_date, 1, 7), channel
ORDER BY month, revenue DESC;

-- 5. Highest-value customers
SELECT
    customer_id,
    customer_name,
    customer_type,
    region,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(net_sales), 2) AS lifetime_revenue,
    ROUND(SUM(gross_profit), 2) AS lifetime_gross_profit
FROM vw_sales_enriched
GROUP BY customer_id, customer_name, customer_type, region
ORDER BY lifetime_revenue DESC
LIMIT 25;
