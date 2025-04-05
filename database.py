import os
import psycopg2
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
        # Don't raise the exception, this will be handled by the caller
        st.error(f"Database connection error: {e}")
        return None

def execute_query(query, params=None):
    """
    Execute a query and return the results as a pandas DataFrame
    """
    import pandas as pd
    from sample_data import get_sample_data
    
    conn = get_db_connection()
    
    # If connection failed, return None to signal caller to use sample data
    if conn is None:
        return None
    
    try:
        df = pd.read_sql(query, conn, params=params)
        return df
    except Exception as e:
        st.error(f"Query execution error: {e}")
        return None
    finally:
        if conn is not None:
            conn.close()

def get_warehouse_data(start_date, end_date):
    """
    Get warehouse data for the specified date range
    If database connection fails, returns None so caller can use sample data
    """
    query = """
    SELECT 
        w.warehouse_id, 
        w.warehouse_name, 
        w.warehouse_location,
        w.team_assignment,
        o.order_id,
        o.product_id,
        o.quantity,
        o.order_date,
        o.expected_delivery_date,
        o.actual_delivery_date,
        o.processing_time,
        o.shipping_time,
        o.order_status,
        o.is_fulfilled,
        p.product_name,
        p.product_category,
        p.brand
    FROM 
        warehouses w
    JOIN 
        orders o ON w.warehouse_id = o.warehouse_id
    JOIN 
        products p ON o.product_id = p.product_id
    WHERE 
        o.order_date BETWEEN %s AND %s
    """
    
    result = execute_query(query, params=[start_date, end_date])
    
    # If database query failed, we'll return None and the app will use sample data
    if result is None:
        st.warning("Database connection failed. Using sample data instead.")
        from sample_data import get_sample_data
        return get_sample_data()
    
    return result
