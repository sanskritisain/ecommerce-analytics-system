-- --- QUERY 7: Running Totals with Window Functions ---
WITH daily_revenue_cte AS (
    SELECT 
        DATE(o.order_date) AS order_date,
        ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS daily_revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.status NOT IN ('CANCELLED')
    GROUP BY DATE(o.order_date)
)
SELECT 
    'GLOBAL' AS region_code, 
    order_date,
    daily_revenue,
    ROUND(SUM(daily_revenue) OVER (ORDER BY order_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS running_total
FROM daily_revenue_cte
ORDER BY order_date ASC;


-- --- QUERY 8: Ranking with DENSE_RANK ---
WITH product_revenue AS (
    SELECT 
        p.category,
        p.product_name,
        ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS total_revenue
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.status NOT IN ('CANCELLED')
    GROUP BY p.category, p.product_name
)
SELECT 
    category,
    product_name,
    total_revenue,
    DENSE_RANK() OVER (PARTITION BY category ORDER BY total_revenue DESC) AS rank_in_category
FROM product_revenue;


-- --- QUERY 9: LAG/LEAD Analysis ---
WITH customer_order_sequence AS (
    SELECT 
        customer_id,
        DATE(order_date) AS order_date,
        LAG(DATE(order_date)) OVER (PARTITION BY customer_id ORDER BY order_date ASC) AS previous_order_date
    FROM orders
),
days_gap_calculation AS (
    SELECT 
        customer_id,
        order_date,
        previous_order_date,
        CASE 
            WHEN previous_order_date IS NULL THEN 0
            ELSE CAST((JULIANDAY(order_date) - JULIANDAY(previous_order_date)) AS INTEGER)
        END AS days_gap
    FROM customer_order_sequence
),
average_gaps AS (
    SELECT 
        customer_id,
        AVG(days_gap) AS avg_customer_gap
    FROM days_gap_calculation
    GROUP BY customer_id
)
SELECT 
    dg.customer_id,
    dg.order_date,
    dg.previous_order_date,
    dg.days_gap,
    CASE 
        WHEN ag.avg_customer_gap > 30 THEN 'At Risk'
        ELSE 'Active'
    END AS status_flag
FROM days_gap_calculation dg
JOIN average_gaps ag ON dg.customer_id = ag.customer_id
ORDER BY dg.customer_id, dg.order_date;


-- --- QUERY 10: CTE with Multiple Levels ---
WITH monthly_customer_spend AS (
    SELECT 
        STRFTIME('%Y-%m', o.order_date) AS sales_month,
        o.customer_id,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS total_spend
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.status NOT IN ('CANCELLED')
    GROUP BY sales_month, o.customer_id
),
customer_tiering AS (
    SELECT 
        sales_month,
        customer_id,
        CASE 
            WHEN total_spend > 10000 THEN 'High'
            WHEN total_spend BETWEEN 5000 AND 10000 THEN 'Medium'
            ELSE 'Low'
        END AS tier
    FROM monthly_customer_spend
)
SELECT 
    sales_month,
    tier,
    COUNT(customer_id) AS customer_count
FROM customer_tiering
GROUP BY sales_month, tier
ORDER BY sales_month ASC, tier DESC;


-- --- QUERY 11: NTILE for Segmentation ---
WITH customer_ltv AS (
    SELECT 
        customer_id,
        ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS total_value
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.status NOT IN ('CANCELLED')
    GROUP BY customer_id
),
quartile_assignment AS (
    SELECT 
        customer_id,
        total_value,
        NTILE(4) OVER (ORDER BY total_value DESC) AS quartile
    FROM customer_ltv
)
SELECT 
    customer_id,
    total_value,
    quartile,
    CASE 
        WHEN quartile = 1 THEN 'Platinum'
        WHEN quartile = 2 THEN 'Gold'
        WHEN quartile = 3 THEN 'Silver'
        ELSE 'Bronze'
    END AS quartile_label
FROM quartile_assignment;


-- --- QUERY 12: Year-over-Year Comparison ---
WITH monthly_revenue AS (
    SELECT 
        CAST(STRFTIME('%Y', order_date) AS INTEGER) AS year,
        CAST(STRFTIME('%m', order_date) AS INTEGER) AS month,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.status NOT IN ('CANCELLED')
    GROUP BY year, month
)
SELECT 
    cur.year,
    cur.month,
    ROUND(cur.revenue, 2) AS revenue,
    ROUND(prev.revenue, 2) AS prev_year_revenue,
    ROUND(COALESCE(((cur.revenue - prev.revenue) / NULLIF(prev.revenue, 0)) * 100, 0), 2) AS yoy_growth_percent
FROM monthly_revenue cur
LEFT JOIN monthly_revenue prev ON cur.year = prev.year + 1 AND cur.month = prev.month
ORDER BY cur.year DESC, cur.month DESC;


-- --- QUERY 13: First/Last Value Analysis ---
WITH ordered_categories AS (
    SELECT 
        o.customer_id,
        p.category,
        o.order_date,
        ROW_NUMBER() OVER (PARTITION BY o.customer_id ORDER BY o.order_date ASC) AS rn_first,
        ROW_NUMBER() OVER (PARTITION BY o.customer_id ORDER BY o.order_date DESC) AS rn_last
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
),
first_cats AS (SELECT customer_id, category AS first_category FROM ordered_categories WHERE rn_first = 1),
last_cats  AS (SELECT customer_id, category AS most_recent_category FROM ordered_categories WHERE rn_last = 1)
SELECT 
    f.customer_id,
    f.first_category,
    l.most_recent_category,
    CASE 
        WHEN f.first_category = l.most_recent_category THEN 'No'
        ELSE 'Yes'
    END AS category_shift
FROM first_cats f
JOIN last_cats l ON f.customer_id = l.customer_id;


-- --- QUERY 14: Cumulative Distribution ---
WITH customer_total_spend AS (
    SELECT 
        customer_id,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS customer_revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.status NOT IN ('CANCELLED')
    GROUP BY customer_id
),
running_sums AS (
    SELECT 
        customer_id,
        customer_revenue,
        SUM(customer_revenue) OVER (ORDER BY customer_revenue DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_revenue,
        SUM(customer_revenue) OVER () AS total_company_revenue
    FROM customer_total_spend
)
SELECT 
    customer_id,
    ROUND(customer_revenue, 2) AS revenue,
    ROUND(cumulative_revenue, 2) AS cumulative_revenue,
    ROUND((cumulative_revenue / total_company_revenue) * 100, 2) AS cumulative_percent
FROM running_sums
ORDER BY revenue DESC;