import pandas as pd
import numpy as np
import datetime
import random

def generate_sample_data():
    """
    Generate sample warehouse, product, and order data for demonstration purposes
    """
    # Set random seed for reproducible results
    np.random.seed(42)
    random.seed(42)
    
    # Define constants
    num_warehouses = 5
    num_products = 20
    num_orders = 200
    
    # Create sample date range (last 60 days)
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=60)
    
    # Generate warehouse data
    warehouses = []
    warehouse_locations = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 
                          'Philadelphia', 'San Antonio', 'San Diego', 'Dallas']
    team_assignments = ['Brand Team', 'Performance Team', 'Social Media Team']
    
    for i in range(1, num_warehouses + 1):
        warehouses.append({
            'warehouse_id': i,
            'warehouse_name': f'Warehouse #{i}',
            'warehouse_location': random.choice(warehouse_locations),
            'team_assignment': random.choice(team_assignments)
        })
    
    # Generate product data
    products = []
    product_categories = ['Electronics', 'Clothing', 'Furniture', 'Food', 'Books']
    brands = ['PremiumBrand', 'ValueChoice', 'LuxuryItems', 'EssentialGoods', 'TrendyStuff']
    
    for i in range(1, num_products + 1):
        products.append({
            'product_id': i,
            'product_name': f'Product {i}',
            'product_category': random.choice(product_categories),
            'brand': random.choice(brands)
        })
    
    # Generate order data
    orders = []
    status_options = ['Processing', 'Shipped', 'Delivered', 'Canceled']
    
    for i in range(1, num_orders + 1):
        # Random dates within range
        order_date = start_date + datetime.timedelta(
            days=random.randint(0, (end_date - start_date).days)
        )
        
        # Random processing time (2-48 hours)
        processing_time = random.uniform(2, 48)
        
        # Random shipping time (1-5 days)
        shipping_time = random.uniform(24, 120)  # In hours
        
        # Expected delivery date
        expected_delivery = order_date + datetime.timedelta(hours=processing_time + shipping_time)
        
        # Actual delivery date (with possible delay)
        delay = random.choice([0, 0, 0, 0, 12, 24, 48])  # 60% on time, 40% delayed
        actual_delivery = expected_delivery + datetime.timedelta(hours=delay)
        
        # Order status
        if (datetime.datetime.now() - order_date).days > 7:
            # Older orders likely delivered
            status = random.choices(
                ['Delivered', 'Canceled'], 
                weights=[0.95, 0.05]
            )[0]
        else:
            # Newer orders might be in process
            status = random.choice(status_options)
        
        # Is order fulfilled
        is_fulfilled = 1 if status == 'Delivered' else 0
        
        orders.append({
            'order_id': i,
            'warehouse_id': random.randint(1, num_warehouses),
            'product_id': random.randint(1, num_products),
            'quantity': random.randint(1, 5),
            'order_date': order_date,
            'expected_delivery_date': expected_delivery,
            'actual_delivery_date': actual_delivery if status == 'Delivered' else None,
            'processing_time': processing_time,
            'shipping_time': shipping_time,
            'order_status': status,
            'is_fulfilled': is_fulfilled
        })
    
    # Create DataFrames
    warehouses_df = pd.DataFrame(warehouses)
    products_df = pd.DataFrame(products)
    orders_df = pd.DataFrame(orders)
    
    # Join data to create the final dataset
    merged_df = orders_df.merge(
        warehouses_df, on='warehouse_id'
    ).merge(
        products_df, on='product_id'
    )
    
    return merged_df

def get_sample_data():
    """
    Return sample data DataFrame for dashboard display
    """
    return generate_sample_data()
