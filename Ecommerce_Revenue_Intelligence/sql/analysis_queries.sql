-- Monthly revenue, orders and AOV
SELECT date_trunc('month',o.invoice_date)::date month,SUM(i.line_revenue) revenue,COUNT(DISTINCT o.invoice_no) orders,SUM(i.line_revenue)/NULLIF(COUNT(DISTINCT o.invoice_no),0) aov FROM retail_analytics.orders o JOIN retail_analytics.order_items i USING(invoice_no) GROUP BY 1 ORDER BY 1;
-- Top products
SELECT p.stock_code,p.description,SUM(i.line_revenue) revenue,SUM(i.quantity) units,COUNT(DISTINCT i.invoice_no) orders FROM retail_analytics.order_items i JOIN retail_analytics.products p USING(stock_code) GROUP BY 1,2 ORDER BY revenue DESC LIMIT 20;
-- Customer purchase value
SELECT o.customer_id,COUNT(DISTINCT o.invoice_no) frequency,SUM(i.line_revenue) monetary,MAX(o.invoice_date) last_purchase FROM retail_analytics.orders o JOIN retail_analytics.order_items i USING(invoice_no) WHERE o.customer_id IS NOT NULL GROUP BY 1 ORDER BY monetary DESC;
