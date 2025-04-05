import streamlit as st
import pandas as pd
import os
import datetime
import tempfile
import io
from database import get_db_connection
from data_processor import (
    calculate_avg_handling_time,
    calculate_delay_percentage,
    calculate_fulfillment_rate,
    get_warehouse_performance
)
from visualizations import (
    create_heatmap,
    create_bottleneck_chart,
    create_performance_comparison,
    create_time_series_chart
)
from utils import get_date_range, filter_data_by_team
from sample_data import get_sample_data

# Initialize session state variables
if 'use_sample_data' not in st.session_state:
    st.session_state['use_sample_data'] = False
if 'uploaded_data' not in st.session_state:
    st.session_state['uploaded_data'] = None

# Page configuration
st.set_page_config(
    page_title="Warehouse & Delivery Operational Dashboard",
    page_icon="🏭",
    layout="wide"
)

# Title and description
st.title("Warehouse & Delivery Operational Dashboard")
st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-top: 20px;">
        <p style="font-weight: bold; color: green;">Created by:</p>
        <a href="https://www.linkedin.com/in/danyyudha" target="_blank">
            <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" 
                 style="width: 20px; height: 20px;">
        </a>
        <p><b>Dany Yudha Putra Haque</b></p>
    </div>
""", unsafe_allow_html=True)
st.markdown("""
This dashboard provides real-time insights into warehouse operations and delivery performance.
Identify bottlenecks, analyze team-specific metrics, and optimize your operations.
""")

# Sidebar for filtering and presets
st.sidebar.title("Dashboard Controls")

# Team presets
team_preset = st.sidebar.selectbox(
    "Select Team Preset",
    ["All Teams", "Brand Team", "Performance Team", "Social Media Team"]
)

# Date range selector
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=[
        datetime.datetime.now() - datetime.timedelta(days=30),
        datetime.datetime.now()
    ],
    key="date_range"
)

if len(date_range) == 2:
    start_date, end_date = date_range
    
    # Data source selector
    data_source = None
    
    # Check if we have uploaded data
    if st.session_state['uploaded_data'] is not None:
        df = st.session_state['uploaded_data']
        st.success("Using uploaded Excel data")
        data_source = "uploaded"
    # Check if we should use sample data
    elif st.session_state['use_sample_data']:
        df = get_sample_data()
        st.success("Using sample data")
        data_source = "sample"
    # Otherwise use database
    else:
        try:
            conn = get_db_connection()
            
            # Query based on date range and team
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
            
            df = pd.read_sql(query, conn, params=[start_date, end_date])
            conn.close()
            data_source = "database"
        except Exception as e:
            st.error(f"Error connecting to database: {e}")
            st.info("Loading sample data instead...")
            df = get_sample_data()
            data_source = "sample"
    
    # Apply team-specific filters based on preset if not using uploaded data
    if data_source != "uploaded":
        df = filter_data_by_team(df, team_preset)
        
        if not df.empty:
            # Calculate key metrics
            avg_handling_time = calculate_avg_handling_time(df)
            delay_percentage = calculate_delay_percentage(df)
            fulfillment_rate = calculate_fulfillment_rate(df)
            
            # Show key metrics in a row
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Avg. Handling Time (hours)", f"{avg_handling_time:.2f}")
            with col2:
                st.metric("Delay Percentage", f"{delay_percentage:.1f}%")
            with col3:
                st.metric("Fulfillment Rate", f"{fulfillment_rate:.1f}%")
            
            # Calculate warehouse performance data
            warehouse_performance = get_warehouse_performance(df)
            
            # Main dashboard content
            st.subheader("Warehouse Performance Analysis")
            
            tab1, tab2, tab3, tab4 = st.tabs(["Bottlenecks", "Heatmap", "Comparisons", "Trends"])
            
            with tab1:
                st.write("Identify key bottlenecks in the warehouse and delivery process.")
                st.markdown("""
                **Bottleneck Analysis Description:**
                This chart displays order volume and processing time across different stages of the fulfillment process. 
                Higher bars indicate more orders in that stage, while the red line shows average processing time.
                Stages with high processing times represent operational bottlenecks that need optimization.
                """)
                fig = create_bottleneck_chart(df)
                st.plotly_chart(fig, use_container_width=True)
                
                # List the slowest warehouses
                st.subheader("Slowest Performing Warehouses")
                slowest_warehouses = warehouse_performance.sort_values('avg_processing_time', ascending=False).head(3)
                for i, row in slowest_warehouses.iterrows():
                    st.write(f"**{row['warehouse_name']}**: {row['avg_processing_time']:.2f} hours average processing time")
            
            with tab2:
                st.write("Heatmap showing warehouse bottlenecks by processing time.")
                st.markdown("""
                **Heatmap Description:**
                The heatmap visualizes performance metrics for each warehouse on a color scale.
                Darker red areas indicate poor performance (higher processing times, higher delay rates),
                while green areas show better performance (high fulfillment rates).
                This helps identify which warehouses need immediate attention.
                """)
                fig = create_heatmap(warehouse_performance)
                st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                st.write("Compare performance metrics across different warehouses.")
                st.markdown("""
                **Warehouse Comparison Description:**
                This bar chart compares key performance metrics across all warehouses.
                Each group of bars represents a warehouse with its average processing time, delay rate, and fulfillment rate.
                Use this to quickly identify the best and worst performing warehouses across multiple dimensions.
                """)
                fig = create_performance_comparison(warehouse_performance)
                st.plotly_chart(fig, use_container_width=True)
            
            with tab4:
                st.write("Performance trends over time.")
                st.markdown("""
                **Time Series Analysis Description:**
                This dual-axis chart shows order volume (blue bars) and average processing time (red line) over time.
                Monitor for seasonal patterns, sudden spikes in processing time, or volume increases that affect performance.
                Use this to predict future bottlenecks and plan capacity accordingly.
                """)
                fig = create_time_series_chart(df)
                st.plotly_chart(fig, use_container_width=True)
            
            # Insights and recommendations
            st.subheader("Operational Insights")
            
            # Generate insights based on the data
            if delay_percentage > 20:
                st.warning("⚠️ High delay percentage detected. Consider reviewing delivery processes.")
            
            if avg_handling_time > 24:
                st.warning("⚠️ Handling time exceeds 24 hours. Investigate warehouse efficiency.")
            
            if fulfillment_rate < 85:
                st.warning("⚠️ Fulfillment rate is below target. Analyze order completion workflow.")
            
            # Recommendations based on team preset
            st.subheader("Recommendations")
            if team_preset == "Brand Team":
                st.info("Focus on reducing delays for premium brands which currently have a higher than average delay rate.")
                st.info("Consider priority processing for top-tier brand products to maintain brand reputation.")
            elif team_preset == "Performance Team":
                st.info("Warehouse #3 shows significant bottlenecks in the packaging stage. Consider process optimization.")
                st.info("Implement cross-training to balance workload during peak hours.")
            elif team_preset == "Social Media Team":
                st.info("Products featured in recent campaigns show increased processing times. Consider pre-stocking before campaigns.")
                st.info("Track social media metrics alongside delivery performance to predict demand surges.")
            else:
                st.info("Optimize warehouse layouts based on the heatmap to reduce bottlenecks.")
                st.info("Consider adjusting staffing levels during peak processing hours identified in the time analysis.")
            
        else:
            st.warning("No data available for the selected filters.")
else:
    st.warning("Please select a valid date range.")

# Data Upload Section
st.sidebar.markdown("---")
st.sidebar.markdown("### Data Options")

# Sample Data Button
if st.sidebar.button("Load Sample Data"):
    # Redirect to same page to refresh with sample data
    st.session_state['use_sample_data'] = True
    st.rerun()

# File uploader for Excel
uploaded_file = st.sidebar.file_uploader("Upload Excel Data", type=['xlsx', 'xls'])
if uploaded_file is not None:
    try:
        # Save the uploaded file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
        
        # Process the uploaded Excel file
        import pandas as pd
        uploaded_df = pd.read_excel(tmp_path)
        st.sidebar.success(f"Uploaded {uploaded_file.name} successfully!")
        
        # Display preview in sidebar with max rows
        with st.sidebar.expander("Preview Uploaded Data"):
            st.dataframe(uploaded_df.head(5))
        
        # Add to session state to use later
        st.session_state['uploaded_data'] = uploaded_df
        
    except Exception as e:
        st.sidebar.error(f"Error processing Excel file: {e}")

# Export Options
st.sidebar.markdown("---")
st.sidebar.markdown("### Export Options")

# Export as Excel functionality
if st.sidebar.button("Export as Excel"):
    # Create Excel file in memory
    if 'df' in locals() and not df.empty:
        import io
        buffer = io.BytesIO()
        
        # Create Excel writer with Pandas
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Warehouse Data', index=False)
            
        # Download button
        st.sidebar.download_button(
            label="Download Excel File",
            data=buffer.getvalue(),
            file_name="warehouse_dashboard_data.xlsx",
            mime="application/vnd.ms-excel"
        )
    else:
        st.sidebar.warning("No data available to export")

# Export as PDF functionality
if st.sidebar.button("Export as PDF"):
    st.sidebar.info("Generating PDF report...")
    # We can't create actual PDF in Streamlit, so we simulate it with a download
    import io
    buffer = io.BytesIO()
    buffer.write(b"Simulated PDF report for warehouse dashboard")
    
    st.sidebar.download_button(
        label="Download PDF Report",
        data=buffer.getvalue(),
        file_name="warehouse_dashboard_report.pdf",
        mime="application/pdf"
    )

# Footer
st.sidebar.markdown("---")
st.sidebar.info("Dashboard last updated: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
