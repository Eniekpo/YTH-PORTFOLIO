-- Q1
SELECT * FROM sales LIMIT 10;

-- Q2
SELECT ROUND(SUM(revenue),2) AS total_revenue,
       ROUND(SUM(profit),2) AS total_profit,
       COUNT(*) AS total_orders,
       SUM(quantity) AS units_sold
FROM sales;

-- Q3
SELECT region,
       ROUND(SUM(revenue),2) AS revenue,
       ROUND(SUM(profit),2) AS profit,
       ROUND(SUM(profit)/NULLIF(SUM(revenue),0),4) AS profit_margin
FROM sales
GROUP BY region
ORDER BY revenue DESC;

-- Q4
SELECT category,
       ROUND(SUM(revenue),2) AS revenue,
       ROUND(SUM(profit),2) AS profit
FROM sales
GROUP BY category
ORDER BY profit DESC;

-- Q5
SELECT year_month,
       ROUND(SUM(revenue),2) AS revenue,
       ROUND(SUM(profit),2) AS profit
FROM sales
GROUP BY year_month
ORDER BY year_month;

-- Q6
SELECT channel,
       COUNT(*) AS orders,
       ROUND(SUM(revenue),2) AS revenue,
       ROUND(SUM(profit),2) AS profit,
       ROUND(AVG(revenue),2) AS avg_order_value
FROM sales
GROUP BY channel
ORDER BY revenue DESC;

-- Q7
SELECT product, ROUND(SUM(revenue),2) AS revenue, ROUND(SUM(profit),2) AS profit
FROM sales
GROUP BY product
ORDER BY revenue DESC
LIMIT 10;

-- Q8
SELECT customer_segment,
       COUNT(*) AS orders,
       ROUND(SUM(revenue),2) AS revenue,
       ROUND(SUM(profit),2) AS profit,
       ROUND(AVG(revenue),2) AS avg_order_value
FROM sales
GROUP BY customer_segment
ORDER BY revenue DESC;

-- Q9
SELECT ROUND(discount*100,0) AS discount_pct,
       COUNT(*) AS orders,
       ROUND(AVG(profit_margin),4) AS avg_profit_margin,
       ROUND(SUM(profit),2) AS profit
FROM sales
GROUP BY discount
ORDER BY discount;

-- Q10
SELECT salesperson, ROUND(SUM(revenue),2) AS revenue, ROUND(SUM(profit),2) AS profit
FROM sales
GROUP BY salesperson
ORDER BY revenue DESC
LIMIT 5;

-- Q11
SELECT order_id, revenue,
       CASE
           WHEN revenue >= 1000 THEN 'High Value'
           WHEN revenue >= 400 THEN 'Medium Value'
           ELSE 'Standard'
       END AS order_value_band
FROM sales;

-- Q12
WITH category_region AS (
    SELECT region, category, SUM(revenue) AS revenue
    FROM sales
    GROUP BY region, category
)
SELECT region, category, ROUND(revenue,2) AS revenue,
       DENSE_RANK() OVER (PARTITION BY region ORDER BY revenue DESC) AS revenue_rank
FROM category_region
ORDER BY region, revenue_rank;

-- Q13
SELECT CAST(strftime('%m', order_date) AS INTEGER) AS month_number,
       ROUND(SUM(CASE WHEN year=2024 THEN revenue ELSE 0 END),2) AS revenue_2024,
       ROUND(SUM(CASE WHEN year=2025 THEN revenue ELSE 0 END),2) AS revenue_2025,
       ROUND(
           (SUM(CASE WHEN year=2025 THEN revenue ELSE 0 END)
           -SUM(CASE WHEN year=2024 THEN revenue ELSE 0 END))
           /NULLIF(SUM(CASE WHEN year=2024 THEN revenue ELSE 0 END),0),
           4
       ) AS yoy_growth
FROM sales
GROUP BY month_number
ORDER BY month_number;

-- Q14
SELECT *
FROM sales
WHERE profit < 0
ORDER BY profit ASC;

-- Q15
-- Multiple answers are valid. Support the insight with query evidence,
-- distinguish observation from recommendation, and avoid unsupported causal claims.
