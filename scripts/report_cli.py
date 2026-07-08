import sys
import sqlite3
import argparse
from datetime import datetime

DB_PATH = 'data/ecommerce_warehouse.db'

def get_db_connection():
    """Handles critical connection exceptions gracefully."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"❌ DATABASE CONNECTION ERROR: Could not link to {DB_PATH}. Details: {e}")
        sys.exit(1)

def validate_date(date_str):
    """Edge Case Handling: Verifies date formatting parameters."""
    try:
        parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
        if parsed_date > datetime.now():
            print(f"⚠️ EDGE CASE WARNING: Provided date '{date_str}' is in the future. Processing anyway...")
        return date_str
    except ValueError:
        print(f"❌ INVALID INPUT ERROR: Date '{date_str}' must follow the 'YYYY-MM-DD' structure layout.")
        sys.exit(1)

def format_as_ascii_table(headers, rows):
    """Formats SQL streams into clean text-based terminal tables without external tools."""
    if not rows:
        print("   [No records found within specified filters]")
        return
    
    # Track the maximum character width needed for each column matrix
    col_widths = [len(h) for h in headers]
    for row in rows:
        for idx, cell in enumerate(row):
            col_widths[idx] = max(col_widths[idx], len(str(cell if cell is not None else "")))
            
    # Draw horizontal boundary outlines
    sep = "+" + "+".join(["-" * (w + 2) for w in col_widths]) + "+"
    
    print(sep)
    print("| " + " | ".join([f"{str(h).ljust(w)}" for h, w in zip(headers, col_widths)]) + " |")
    print(sep)
    for row in rows:
        print("| " + " | ".join([f"{str(cell if cell is not None else '').ljust(w)}" for cell, w in zip(row, col_widths)]) + " |")
    print(sep)

def run_edge_case_tests(conn):
    """Part 5: Automated validation scripts verifying pipeline guardrails."""
    print("\n🕵️ Executing Core System Edge Case Audits...")
    cursor = conn.cursor()
    
    # Test 1: Check for anomalies where discount > 100%
    cursor.execute("SELECT COUNT(*) FROM order_items WHERE discount_percent > 100")
    bad_discounts = cursor.fetchone()[0]
    print(f" -> Edge Case Audit 1 (Discount > 100%): Found {bad_discounts} rows. " + ("✅ PASSED" if bad_discounts == 0 else "❌ FAILED"))

    # Test 2: Check for structural quantity anomalies equal to exactly zero
    cursor.execute("SELECT COUNT(*) FROM order_items WHERE quantity = 0")
    zero_qty = cursor.fetchone()[0]
    print(f" -> Edge Case Audit 2 (Quantity == 0): Found {zero_qty} rows. " + ("✅ PASSED" if zero_qty == 0 else "❌ FAILED"))

    # Test 3: Check for referential isolation links (Orphan records)
    cursor.execute("SELECT COUNT(*) FROM order_items WHERE order_id NOT IN (SELECT order_id FROM orders)")
    orphans = cursor.fetchone()[0]
    print(f" -> Edge Case Audit 3 (Referential Integrity): Found {orphans} orphaned item records. " + ("✅ PASSED" if orphans == 0 else "❌ FAILED"))

def generate_business_summary(report_type, start_date, end_date):
    """Aggregates metrics and applies cross-period comparative variances dynamically."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    run_edge_case_tests(conn)
    
    print(f"\n📈 COMPILING E-COMMERCE SUMMARY REPORT [{report_type.upper()}]")
    print(f"📅 Filter Range: {start_date} to {end_date}")
    
   
    metrics_query = """
        SELECT 
            COUNT(DISTINCT o.order_id) AS total_orders,
            ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS net_revenue,
            COUNT(DISTINCT o.customer_id) AS unique_customers
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        WHERE DATE(o.order_date) BETWEEN ? AND ? AND o.status NOT IN ('CANCELLED')
    """
    cursor.execute(metrics_query, (start_date, end_date))
    res = cursor.fetchone()
    
    total_orders = res['total_orders'] or 0
    net_revenue = res['net_revenue'] or 0.0
    unique_customers = res['unique_customers'] or 0
    
    if total_orders == 0:
        print("\n🛑 REPORT ALERT: Zero valid operational cycles found for this exact interval filter.")
        conn.close()
        return

    top_items_query = """
        SELECT 
            p.product_name,
            SUM(oi.quantity) AS units_sold,
            ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS product_revenue
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        JOIN orders o ON oi.order_id = o.order_id
        WHERE DATE(o.order_date) BETWEEN ? AND ? AND o.status NOT IN ('CANCELLED')
        GROUP BY p.product_id, p.product_name
        ORDER BY units_sold DESC
        LIMIT 3
    """
    cursor.execute(top_items_query, (start_date, end_date))
    top_products_rows = cursor.fetchall()
    
    baseline_query = """
        SELECT ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS revenue
        FROM orders o JOIN order_items oi ON o.order_id = oi.order_id
        WHERE DATE(o.order_date) BETWEEN ? AND ? AND o.status NOT IN ('CANCELLED')
    """
    
    cursor.execute(baseline_query, ("2020-01-01", start_date)) 
    past_rev_res = cursor.fetchone()
    past_revenue = past_rev_res[0] or 0.0
    
   
    if past_revenue > 0:
        pct_change = round(((net_revenue - past_revenue) / past_revenue) * 100, 2)
        comparison_str = f"{pct_change}% shift relative to previous baseline benchmarks"
    else:
        comparison_str = "Baseline metrics unavailable for prior timeline frameworks"
    print("\n" + "="*55)
    print("                EXECUTIVE BUSINESS KPI REPORT             ")
    print("="*55)
    print(f" Total Registered Revenue : ${net_revenue:,}")
    print(f" Total Confirmed Orders   : {total_orders}")
    print(f" Total Unique Customers   : {unique_customers}")
    print(f" Operational Context      : {comparison_str}")
    print("="*55)
    
    print("\n⭐ TOP 3 LEADING MERCHANDISE LINES:")
    format_as_ascii_table(
        ["Product Name", "Units Distributed", "Net Revenue Generation"],
        [[r[0], r[1], f"${r[2]:,}"] for r in top_products_rows]
    )
    conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="E-commerce Enterprise Reporting Engine Module API Interface")
    parser.add_argument('--report', required=True, choices=['daily', 'weekly', 'monthly'], help="Report frequency cycle type")
    parser.add_argument('--start', required=True, help="Start evaluation interval (YYYY-MM-DD)")
    parser.add_argument('--end', required=True, help="End evaluation interval (YYYY-MM-DD)")
    
    args = parser.parse_args()
    
    s_dt = validate_date(args.start)
    e_dt = validate_date(args.end)
    
    if s_dt > e_dt:
        print("❌ CONTEXT BOUNDARY ERROR: The start date cannot track chronologically past the chosen end boundary.")
        sys.exit(1)
        
    generate_business_summary(args.report, s_dt, e_dt)