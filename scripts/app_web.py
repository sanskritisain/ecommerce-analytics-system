import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="E-Commerce Order Analytics System", layout="wide")
st.title("🚀 E-Commerce Analytics Intelligence Dashboard")
st.markdown("---")

DB_PATH = 'data/ecommerce_warehouse.db'

def run_query(query):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn)

st.sidebar.header("🔍 Filter Analytics Control Room")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2024-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("2026-12-31"))

st.subheader("📌 Executive Key Performance Indicators")
kpi_query = f"""
    SELECT COUNT(DISTINCT o.order_id) as total_orders,
           COUNT(DISTINCT o.customer_id) as total_customers,
           ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) as total_revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_date BETWEEN '{start_date}' AND '{end_date}'
"""
kpi_df = run_query(kpi_query)

if not kpi_df.empty and kpi_df['total_orders'].iloc[0] > 0:
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Net Revenue Generation", f"${kpi_df['total_revenue'].iloc[0]:,}")
    col2.metric("📦 Confirmed Distributed Orders", f"{kpi_df['total_orders'].iloc[0]:,}")
    col3.metric("👥 Active Unique Customers", f"{kpi_df['total_customers'].iloc[0]:,}")
else:
    st.warning("⚠️ Defined target temporal ranges contain 0 active database modifications.")

st.markdown("---")
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🛍️ Financial Performance by Category")
    rev_query = """
        SELECT p.category, 
               ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS total_revenue
        FROM products p
        JOIN order_items oi ON p.product_id = oi.product_id
        GROUP BY p.category ORDER BY total_revenue DESC
    """
    rev_df = run_query(rev_query)
    fig_pie = px.pie(rev_df, values='total_revenue', names='category', title="Revenue Contribution Matrix", hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)

with col_right:
    st.subheader("🎯 Customer LTV Quartile Distribution")
    ltv_query = """
        WITH ltv AS (
            SELECT customer_id, SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS val
            FROM orders o JOIN order_items oi ON o.order_id = oi.order_id GROUP BY customer_id
        ), q AS (
            SELECT customer_id, val, NTILE(4) OVER (ORDER BY val DESC) as quartile FROM ltv
        )
        SELECT CASE WHEN quartile=1 THEN 'Platinum' WHEN quartile=2 THEN 'Gold' WHEN quartile=3 THEN 'Silver' ELSE 'Bronze' END as Segment,
               COUNT(*) as Total_Customers FROM q GROUP BY Segment
    """
    ltv_df = run_query(ltv_query)
    fig_bar = px.bar(ltv_df, x='Segment', y='Total_Customers', color='Segment', title="User Cohorts Segmented via NTILE()")
    st.plotly_chart(fig_bar, use_container_width=True)
