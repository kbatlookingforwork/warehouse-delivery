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
            conn = psycopg2.connect(database_url)
            return conn
        
        # Otherwise use individual connection parameters
        conn = psycopg2.connect(
            host=os.getenv("PGHOST", "localhost"),
            database=os.getenv("PGDATABASE", "postgres"),
            user=os.getenv("PGUSER", "postgres"),
            password=os.getenv("PGPASSWORD", ""),
            port=os.getenv("PGPORT", "5432")
        )
        return conn
    except Exception as e:
        st.error(f"Database connection error: {e}")
        raise

def execute_query(query, params=None):
    """
    Execute a query and return the results as a pandas DataFrame
    """
    import pandas as pd
    
    conn = get_db_connection()
    try:
        df = pd.read_sql(query, conn, params=params)
        return df
    except Exception as e:
        st.error(f"Query execution error: {e}")
        raise
    finally:
        conn.close()

def get_warehouse_data(start_date, end_date):
    """
    Get warehouse data for the specified date range
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
    
    return execute_query(query, params=[start_date, end_date])
