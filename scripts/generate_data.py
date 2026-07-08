import csv 
import random 
from datetime import datetime, timedelta
from faker import Faker
fake=Faker()
random.seed(42)
NUM_ROWS=600
#customer data generation
customers=[]
customer_ids=[f"CUST_{str(i).zfill(4)}" for i in range(1, NUM_ROWS + 1)]
for i, cid in enumerate(customer_ids):
    name = fake.name()
    email = fake.email()
    if i < int(NUM_ROWS * 0.02):
        if random.choice([True, False]):
            email = email.replace("@", "") 
        else:
            email = f"{fake.word()}.com"
    reg_date = fake.date_between(start_date='-2y', end_date='today').strftime('%Y-%m-%d')
    c_type = random.choice(['REGULAR', 'PREMIUM', 'VIP']) 
    customers.append([cid, name , email,reg_date,c_type]) 
with open('data/raw/customers.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['customer_id', 'customer_name', 'email', 'registration_date', 'customer_type'])
    writer.writerows(customers)

#product data generation 
products = []
product_ids = [f"PROD_{str(i).zfill(4)}" for i in range(1, NUM_ROWS + 1)]
categories = {
        'Electronics': ['Phones', 'Laptops', 'Accessories'],
        'Clothing': ['Men', 'Women', 'Kids'],
        'Home': ['Kitchen', 'Furniture', 'Decor'],
        'Books': ['Fiction', 'Sci-Fi', 'Biographies']
    }
    
for pid in product_ids:
    cat = random.choice(list(categories.keys()))
    subcat = random.choice(categories[cat])
        
    p_name = fake.words(nb=2)
        
    if random.random() < 0.1:
        p_name_str = f"  {p_name[0].upper()} {p_name[1].lower()}   "
    else:
        p_name_str = f"{p_name[0].title()} {p_name[1].title()}"
        
        cost_price = round(random.uniform(5.0, 500.0), 2)
        products.append([pid, p_name_str, cat, subcat, cost_price])
        
with open('data/raw/products.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['product_id', 'product_name', 'category', 'subcategory', 'cost_price'])
    writer.writerows(products)

#order data generation 
orders = []
order_ids = [f"ORD_{str(i).zfill(5)}" for i in range(1, NUM_ROWS + 1)]
statuses = ['PLACED', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'RETURNED']
    
for i, oid in enumerate(order_ids):
        
    cid = "" if i < int(NUM_ROWS * 0.05) else random.choice(customer_ids)
    status = random.choice(statuses)
        
    base_date = datetime.now() - timedelta(days=random.randint(0, 730))

    if random.random() < 0.05:
        order_date = base_date.strftime('%d-%m-%Y')
    else:
        order_date = base_date.strftime('%Y-%m-%d %H:%M:%S')
            
        orders.append([oid, cid, status, order_date])
        
with open('data/raw/orders.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['order_id', 'customer_id', 'status', 'order_date'])
    writer.writerows(orders)

# ORDER ITEMS DATA GENERATION
order_items = []
for i in range(1, NUM_ROWS + 200):
    item_id = f"ITEM_{str(i).zfill(5)}"
        
       
    oid = "ORD_99999" if random.random() < 0.02 else random.choice(order_ids)
    pid = random.choice(product_ids)
        
    
    qty = random.randint(-5, -1) if random.random() < 0.03 else random.randint(1, 5)
        
    unit_price = round(random.uniform(10.0, 600.0), 2)
    discount = round(random.uniform(0.0, 30.0), 2)
        
    order_items.append([item_id, oid, pid, qty, unit_price, discount])
        
with open('data/raw/order_items.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['order_item_id', 'order_id', 'product_id', 'quantity', 'unit_price', 'discount_percent'])
    writer.writerows(order_items)

