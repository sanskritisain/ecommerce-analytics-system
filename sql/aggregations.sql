-- --- QUERY 1: Total revenue per category ---
-- Formula: revenue = quantity * unit_price * (1 - discount_percent/100)
SELECT 
    p.category,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS total_revenue
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status NOT IN ('CANCELLED') 
ORDER BY total_revenue DESC;

-- --- QUERY 2: Top 10 customers by total order value ---
SELECT 
    c.customer_id,
    c.customer_name,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS total_order_value
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status NOT IN ('CANCELLED')
GROUP BY c.customer_id, c.customer_name
ORDER BY total_order_value DESC
LIMIT 10;

-- --- QUERY 3: Month-wise order count for the last 12 months ---
-- Uses STRFTIME to extract 'YYYY-MM' from the standardized date
SELECT 
    STRFTIME('%Y-%m', o.order_date) AS order_month,
    COUNT(DISTINCT o.order_id) AS total_orders
FROM orders o
WHERE o.order_date >= DATE('now', '-12 months')
GROUP BY order_month
ORDER BY order_month DESC;

-- --- QUERY 4: Find customers who placed orders but never had any item delivered ---
-- Finds customers whose orders never hit 'DELIVERED' status
SELECT 
    c.customer_id,
    c.customer_name
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name
HAVING SUM(CASE WHEN o.status = 'DELIVERED' THEN 1 ELSE 0 END) = 0;


-- --- QUERY 5: Products that were ordered but had more returns than purchases ---
-- Remember: negative quantity in order_items represents returns
SELECT 
    p.product_id,
    p.product_name,
    SUM(CASE WHEN oi.quantity > 0 THEN oi.quantity ELSE 0 END) AS total_purchased,
    SUM(CASE WHEN oi.quantity < 0 THEN ABS(oi.quantity) ELSE 0 END) AS total_returned
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id, p.product_name
HAVING total_returned > total_purchased;


-- --- QUERY 6: Calculate the return rate (returned items / total items) per category ---
-- Formula: SUM(Returned Units) / SUM(All Units). We check for 0 to prevent division errors.
SELECT 
    p.category,
    SUM(CASE WHEN oi.quantity < 0 THEN ABS(oi.quantity) ELSE 0 END) AS returned_items,
    SUM(CASE WHEN oi.quantity > 0 THEN oi.quantity ELSE 0 END) AS purchased_items,
    ROUND(
        CAST(SUM(CASE WHEN oi.quantity < 0 THEN ABS(oi.quantity) ELSE 0 END) AS REAL) / 
        NULLIF(SUM(CASE WHEN oi.quantity > 0 THEN oi.quantity ELSE 0 END), 0) * 100, 
        2
    ) AS return_rate_percent
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY return_rate_percent DESC;