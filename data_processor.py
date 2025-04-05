import pandas as pd
import numpy as np

def calculate_avg_handling_time(df):
    """
    Calculate the average handling time (in hours) for all orders
    """
    # Ensure processing_time is numeric
    df['processing_time_numeric'] = pd.to_numeric(df['processing_time'], errors='coerce')
    
    # Calculate average handling time in hours
    avg_time = df['processing_time_numeric'].mean()
    
    return avg_time if not pd.isna(avg_time) else 0

def calculate_delay_percentage(df):
    """
    Calculate the percentage of orders that were delayed
    """
    if df.empty:
        return 0
    
    # Convert date columns to datetime if they aren't already
    for col in ['expected_delivery_date', 'actual_delivery_date']:
        if df[col].dtype != 'datetime64[ns]':
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Calculate delays
    df['is_delayed'] = (df['actual_delivery_date'] > df['expected_delivery_date']).astype(int)
    
    # Calculate delay percentage
    delay_percentage = (df['is_delayed'].sum() / len(df)) * 100
    
    return delay_percentage

def calculate_fulfillment_rate(df):
    """
    Calculate the fulfillment rate (percentage of orders fulfilled)
    """
    if df.empty:
        return 0
    
    # Ensure is_fulfilled is properly cast to avoid type errors
    if 'is_fulfilled' in df.columns:
        # Convert to integer/boolean if it's a string
        if df['is_fulfilled'].dtype == 'object':
            df['is_fulfilled'] = df['is_fulfilled'].map({'True': 1, 'False': 0, True: 1, False: 0})
        
        # Calculate fulfillment rate
        fulfill_rate = (df['is_fulfilled'].sum() / len(df)) * 100
        return fulfill_rate
    else:
        # Alternative calculation using order_status if is_fulfilled isn't available
        fulfilled_statuses = ['delivered', 'completed', 'fulfilled']
        df['fulfilled'] = df['order_status'].str.lower().isin(fulfilled_statuses).astype(int)
        fulfill_rate = (df['fulfilled'].sum() / len(df)) * 100
        return fulfill_rate

def get_warehouse_performance(df):
    """
    Calculate performance metrics for each warehouse
    """
    if df.empty:
        return pd.DataFrame()
    
    # Ensure processing_time is numeric
    df['processing_time_numeric'] = pd.to_numeric(df['processing_time'], errors='coerce')
    
    # Convert date columns to datetime if needed
    for col in ['expected_delivery_date', 'actual_delivery_date']:
        if df[col].dtype != 'datetime64[ns]':
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Add delay flag
    df['is_delayed'] = (df['actual_delivery_date'] > df['expected_delivery_date']).astype(int)
    
    # Handle is_fulfilled data type
    if df['is_fulfilled'].dtype == 'object':
        df['is_fulfilled'] = df['is_fulfilled'].map({'True': 1, 'False': 0, True: 1, False: 0})
    
    # Group by warehouse and calculate metrics
    warehouse_performance = df.groupby(['warehouse_id', 'warehouse_name', 'warehouse_location']).agg({
        'processing_time_numeric': 'mean',
        'is_delayed': 'mean',
        'is_fulfilled': 'mean',
        'order_id': 'count'
    }).reset_index()
    
    # Rename columns
    warehouse_performance.columns = [
        'warehouse_id', 'warehouse_name', 'warehouse_location', 
        'avg_processing_time', 'delay_rate', 'fulfillment_rate', 'order_count'
    ]
    
    # Convert rates to percentages
    warehouse_performance['delay_rate'] = warehouse_performance['delay_rate'] * 100
    warehouse_performance['fulfillment_rate'] = warehouse_performance['fulfillment_rate'] * 100
    
    # Calculate an overall performance score (lower is better)
    warehouse_performance['performance_score'] = (
        warehouse_performance['avg_processing_time'] * 0.4 + 
        warehouse_performance['delay_rate'] * 0.4 - 
        warehouse_performance['fulfillment_rate'] * 0.2
    )
    
    return warehouse_performance

def identify_bottlenecks(df):
    """
    Identify bottlenecks in the warehouse and delivery process
    """
    if df.empty:
        return pd.DataFrame()
    
    # Create processing stages based on processing time
    df['processing_time_numeric'] = pd.to_numeric(df['processing_time'], errors='coerce')
    
    # Define processing stages (example)
    df['stage'] = pd.cut(
        df['processing_time_numeric'],
        bins=[0, 2, 6, 12, 24, float('inf')],
        labels=['Rapid', 'Normal', 'Extended', 'Delayed', 'Critical']
    )
    
    # Analyze bottlenecks by warehouse and stage
    bottleneck_analysis = df.groupby(['warehouse_id', 'warehouse_name', 'stage']).size().reset_index(name='count')
    
    return bottleneck_analysis

def analyze_trends(df):
    """
    Analyze trends over time
    """
    if df.empty:
        return pd.DataFrame()
    
    # Ensure order_date is datetime
    if df['order_date'].dtype != 'datetime64[ns]':
        df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
    
    # Add date features
    df['date'] = df['order_date'].dt.date
    df['month'] = df['order_date'].dt.month
    df['day_of_week'] = df['order_date'].dt.dayofweek
    
    # Ensure processing_time is numeric
    df['processing_time_numeric'] = pd.to_numeric(df['processing_time'], errors='coerce')
    
    # Analyze trends by date
    trend_analysis = df.groupby('date').agg({
        'processing_time_numeric': 'mean',
        'order_id': 'count'
    }).reset_index()
    
    trend_analysis.columns = ['date', 'avg_processing_time', 'order_count']
    
    return trend_analysis
