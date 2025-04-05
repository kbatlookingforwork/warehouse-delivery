import os
import psycopg2
import pandas as pd
from datetime import datetime, timedelta
import random
import streamlit as st

def get_db_connection():
    """
    Create a connection to the PostgreSQL database using environment variables
    """
    try:
        # Try using the complete DATABASE_URL if available
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            # Modify the connection parameters to ensure proper connection
            conn = psycopg2.connect(
                database_url,
                # Set a timeout to avoid long connection attempts
                connect_timeout=3
            )
            return conn
        
        # Otherwise use individual connection parameters with explicit host
        conn = psycopg2.connect(
            host=os.getenv("PGHOST", "127.0.0.1"),  # Use IP directly instead of 'localhost'
            database=os.getenv("PGDATABASE", "postgres"),
            user=os.getenv("PGUSER", "postgres"),
            password=os.getenv("PGPASSWORD", ""),
            port=os.getenv("PGPORT", "5432"),
            # Set a timeout to avoid long connection attempts
            connect_timeout=3
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def setup_database():
    """
    Set up the database tables if they don't exist
    """
    conn = get_db_connection()
    if conn is None:
        print("Could not connect to database. Setup failed.")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Create warehouses table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS warehouses (
            warehouse_id SERIAL PRIMARY KEY,
            warehouse_name VARCHAR(100) NOT NULL,
            warehouse_location VARCHAR(100) NOT NULL,
            team_assignment VARCHAR(50) NOT NULL
        )
        """)
        
        # Create products table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id SERIAL PRIMARY KEY,
            product_name VARCHAR(100) NOT NULL,
            product_category VARCHAR(50) NOT NULL,
            brand VARCHAR(50) NOT NULL
        )
        """)
        
        # Create orders table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id SERIAL PRIMARY KEY,
            warehouse_id INTEGER REFERENCES warehouses(warehouse_id),
            product_id INTEGER REFERENCES products(product_id),
            quantity INTEGER NOT NULL,
            order_date DATE NOT NULL,
            expected_delivery_date DATE NOT NULL,
            actual_delivery_date DATE,
            processing_time FLOAT NOT NULL,
            shipping_time FLOAT,
            order_status VARCHAR(20) NOT NULL,
            is_fulfilled BOOLEAN NOT NULL
        )
        """)
        
        # Commit the changes
        conn.commit()
        
        # Check if tables have data
        try:
            cursor.execute("SELECT COUNT(*) FROM warehouses")
            result = cursor.fetchone()
            warehouse_count = result[0] if result else 0
        except Exception as e:
            # If the table doesn't exist yet, we'll get an error
            print(f"Error checking warehouse count: {e}")
            warehouse_count = 0
        
        if warehouse_count == 0:
            print("Inserting sample data into the database...")
            # Insert sample data
            insert_sample_data(conn)
        else:
            print(f"Database already has {warehouse_count} warehouses. Skipping sample data insertion.")
        
        conn.close()
        return True
    
    except Exception as e:
        print(f"Error setting up database: {e}")
        if conn:
            conn.close()
        return False

def insert_sample_data(conn):
    """
    Insert sample data into the database
    """
    cursor = conn.cursor()
    
    # Insert warehouses
    warehouses = [
        ('Central Warehouse', 'Chicago, IL', 'Performance Team'),
        ('East Coast Facility', 'Newark, NJ', 'Brand Team'),
        ('West Coast Depot', 'San Francisco, CA', 'Social Media Team'),
        ('Southern Distribution', 'Houston, TX', 'Performance Team'),
        ('Midwest Logistics', 'Columbus, OH', 'Brand Team')
    ]
    
    for w in warehouses:
        cursor.execute(
            "INSERT INTO warehouses (warehouse_name, warehouse_location, team_assignment) VALUES (%s, %s, %s)",
            w
        )
    
    # Insert products
    products = [
        ('Premium Watch', 'Accessories', 'LuxBrand'),
        ('Wireless Headphones', 'Electronics', 'AudioTech'),
        ('Running Shoes', 'Footwear', 'SportLife'),
        ('Protein Powder', 'Nutrition', 'FitLife'),
        ('Smart Speaker', 'Electronics', 'HomeConnect'),
        ('Leather Wallet', 'Accessories', 'LuxBrand'),
        ('Fitness Tracker', 'Electronics', 'TechFit'),
        ('Coffee Maker', 'Home Goods', 'MorningBrew'),
        ('Desktop Monitor', 'Electronics', 'TechPro'),
        ('Backpack', 'Accessories', 'TravelEase')
    ]
    
    for p in products:
        cursor.execute(
            "INSERT INTO products (product_name, product_category, brand) VALUES (%s, %s, %s)",
            p
        )
    
    # Get the IDs of inserted warehouses and products
    cursor.execute("SELECT warehouse_id FROM warehouses")
    warehouse_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT product_id FROM products")
    product_ids = [row[0] for row in cursor.fetchall()]
    
    # Generate 200 random orders over the last 30 days
    orders = []
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    order_statuses = ['Processing', 'Shipped', 'Delivered', 'Cancelled']
    
    for i in range(200):
        # Random dates within the last 30 days
        order_date = start_date + timedelta(days=random.randint(0, 30))
        expected_delivery_date = order_date + timedelta(days=random.randint(1, 7))
        
        # Processing time between 1 and 36 hours
        processing_time = round(random.uniform(1, 36), 2)
        
        # 80% of orders are fulfilled
        is_fulfilled = random.random() < 0.8
        
        # Set status and actual delivery date based on fulfillment
        if is_fulfilled:
            order_status = 'Delivered'
            shipping_time = round(random.uniform(12, 72), 2)
            actual_delivery_date = expected_delivery_date
            
            # 70% of orders arrive on time, 30% are delayed
            if random.random() < 0.3:
                actual_delivery_date += timedelta(days=random.randint(1, 3))
                
        else:
            # Not fulfilled orders are either processing or shipped
            order_status = 'Processing' if random.random() < 0.5 else 'Shipped'
            shipping_time = None if order_status == 'Processing' else round(random.uniform(12, 48), 2)
            actual_delivery_date = None
        
        orders.append((
            random.choice(warehouse_ids),
            random.choice(product_ids),
            random.randint(1, 5),  # quantity
            order_date,
            expected_delivery_date,
            actual_delivery_date,
            processing_time,
            shipping_time,
            order_status,
            is_fulfilled
        ))
    
    # Insert orders
    for o in orders:
        cursor.execute("""
        INSERT INTO orders (
            warehouse_id, product_id, quantity, 
            order_date, expected_delivery_date, actual_delivery_date,
            processing_time, shipping_time, order_status, is_fulfilled
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, o)
    
    # Commit all changes
    conn.commit()
    print(f"Inserted {len(warehouses)} warehouses, {len(products)} products, and {len(orders)} orders")

if __name__ == "__main__":
    setup_database()
