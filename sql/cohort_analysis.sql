-- --- QUERY 15: Complex CTE: Cohort Analysis ---
WITH customer_signup_cohort AS (
    -- Group customers by their registration/signup month
    SELECT 
        customer_id,
        STRFTIME('%Y-%m', registration_date) AS cohort_month
    FROM customers
),
customer_activity_months AS (
    -- Track unique months in which each customer placed an active order
    SELECT DISTINCT
        o.customer_id,
        STRFTIME('%Y-%m', o.order_date) AS activity_month
    FROM orders o
    WHERE o.status NOT IN ('CANCELLED')
),
cohort_size AS (
    -- Calculate total unique starting customers per cohort group (Month 0 base)
    SELECT 
        cohort_month,
        COUNT(DISTINCT customer_id) AS total_cohort_size
    FROM customer_signup_cohort
    GROUP BY cohort_month
),
cohort_retention_intervals AS (
    -- Calculate chronological monthly distance between signup and order month
    SELECT 
        c.cohort_month,
        a.activity_month,
        CAST((
            (STRFTIME('%Y', a.activity_month) - STRFTIME('%Y', c.cohort_month)) * 12 +
            (STRFTIME('%m', a.activity_month) - STRFTIME('%m', c.cohort_month))
        ) AS INTEGER) AS period_month,
        COUNT(DISTINCT a.customer_id) AS active_users
    FROM customer_signup_cohort c
    JOIN customer_activity_months a ON c.customer_id = a.customer_id
    WHERE a.activity_month >= c.cohort_month
    GROUP BY c.cohort_month, period_month
)
SELECT 
    r.cohort_month,
    s.total_cohort_size AS month_0_users,
    SUM(CASE WHEN r.period_month = 1 THEN r.active_users ELSE 0 END) AS month_1_users,
    SUM(CASE WHEN r.period_month = 2 THEN r.active_users ELSE 0 END) AS month_2_users,
    SUM(CASE WHEN r.period_month = 3 THEN r.active_users ELSE 0 END) AS month_3_users,
    ROUND(SUM(CASE WHEN r.period_month = 1 THEN r.active_users ELSE 0 END) * 100.0 / s.total_cohort_size, 2) AS m1_retention_rate_pct,
    ROUND(SUM(CASE WHEN r.period_month = 2 THEN r.active_users ELSE 0 END) * 100.0 / s.total_cohort_size, 2) AS m2_retention_rate_pct,
    ROUND(SUM(CASE WHEN r.period_month = 3 THEN r.active_users ELSE 0 END) * 100.0 / s.total_cohort_size, 2) AS m3_retention_rate_pct
FROM cohort_retention_intervals r
JOIN cohort_size s ON r.cohort_month = s.cohort_month
WHERE r.period_month BETWEEN 0 AND 3
GROUP BY r.cohort_month, s.total_cohort_size
ORDER BY r.cohort_month ASC;


-- --- QUERY 16: Self-Join with Window Function ---
WITH customer_ordered_journey AS (
    SELECT 
        order_id,
        customer_id,
        order_date,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date ASC) AS order_sequence_number
    FROM orders
    WHERE status NOT IN ('CANCELLED')
)
SELECT 
    current_order.customer_id,
    current_order.order_id AS current_order_id,
    current_order.order_date AS current_order_date,
    next_order.order_id AS subsequent_order_id,
    next_order.order_date AS subsequent_order_date,
    CAST((JULIANDAY(next_order.order_date) - JULIANDAY(current_order.order_date)) AS INTEGER) AS interval_days_between
FROM customer_ordered_journey current_order
LEFT JOIN customer_ordered_journey next_order 
    ON current_order.customer_id = next_order.customer_id 
    AND current_order.order_sequence_number + 1 = next_order.order_sequence_number
ORDER BY current_order.customer_id, current_order.order_sequence_number;