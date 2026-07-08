import pandas as pd 
import re 
df_cust=pd.read_csv('data/raw/customers.csv')
df_prod=pd.read_csv('data/raw/products.csv')
df_ord=pd.read_csv('data/raw/orders.csv')
df_items=pd.read_csv('data/raw/order_items.csv')
print(f"Initial Row Counts -> Customers: {len(df_cust)}, Products: {len(df_prod)}, Orders: {len(df_ord)}, Items: {len(df_items)}")
#cleaning customer data table
email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
is_valid_email=df_cust['email'].astype(str).apply(lambda x: bool(re.match(email_pattern,x)))
bad_emails_count=len(df_cust)-is_valid_email.sum()
print(f" -> Found {bad_emails_count} invalid emails. Removing those records.")
df_cust = df_cust[is_valid_email]
print(f" -> Cleaned Customers Row Count: {len(df_cust)}")
#cleaning product data table
df_prod['product_name']=df_prod['product_name'].astype(str).str.strip()
df_prod['product_name']=df_prod['product_name'].str.title()
print(f" -> Cleaned Products Row Count: {len(df_prod)}")
#cleaning order table 
initial_orders=len(df_ord)
df_ord=df_ord.dropna(subset=['customer_id'])
null_dropped=initial_orders-len(df_ord)
def parse_date_safely(date_str):
    try:
        return pd.to_datetime(date_str, format='%Y-%m-%d %H:%M:%S')
    except:
        try:
            return pd.to_datetime(date_str, format='%d-%m-%Y')
        except:
            return pd.NaT 
df_ord['order_date'] = df_ord['order_date'].astype(str).apply(parse_date_safely)
df_ord = df_ord.dropna(subset=['order_date'])
print(f" -> Cleaned Orders Row Count: {len(df_ord)}")
#cleaning order items table 
initial_items=len(df_items)
is_valid_order_link=df_items['order_id'].isin(df_ord['order_id'])
df_items = df_items[is_valid_order_link]
orphans_removed = initial_items - len(df_items)
print(f" -> Found and removed {orphans_removed} orphaned items rows (Referential Integrity check).")
print(f" -> Cleaned Order Items Row Count: {len(df_items)}")
print("\nSaving clean datasets to data/cleaned/ folder...")
df_cust.to_csv('data/cleaned/customers_clean.csv', index=False)
df_prod.to_csv('data/cleaned/products_clean.csv', index=False)
df_ord.to_csv('data/cleaned/orders_clean.csv', index=False)
df_items.to_csv('data/cleaned/order_items_clean.csv', index=False)

print("\n DATA CLEANING PIPELINE COMPLETELY SUCCESSFUL!")


import sqlite3
print("\nLoading clean data directly into SQL Warehouse...")

conn = sqlite3.connect('data/ecommerce_warehouse.db')
cursor = conn.cursor()

with open('sql/schema.sql', 'r') as f:
    schema_sql = f.read()
cursor.executescript(schema_sql)

df_cust.to_sql('customers', conn, if_exists='append', index=False)
df_prod.to_sql('products', conn, if_exists='append', index=False)
df_ord.to_sql('orders', conn, if_exists='append', index=False)
df_items.to_sql('order_items', conn, if_exists='append', index=False)

conn.commit()
conn.close()
print("🚀 SUCCESS: SQL Warehouse updated and ready for analysis!")