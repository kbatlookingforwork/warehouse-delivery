import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def create_heatmap(warehouse_performance):
    """
    Create a heatmap of warehouse performance metrics
    """
    if warehouse_performance.empty:
        # Return empty figure if no data
        return go.Figure()
    
    # Create a pivot table for the heatmap
    z_data = warehouse_performance.set_index('warehouse_name')[['avg_processing_time', 'delay_rate', 'fulfillment_rate']]
    
    # Create heatmap using plotly
    fig = go.Figure(data=go.Heatmap(
        z=z_data.values,
        x=['Avg Processing Time (hrs)', 'Delay Rate (%)', 'Fulfillment Rate (%)'],
        y=z_data.index,
        colorscale='RdYlGn_r',
        reversescale=True,
    ))
    
    fig.update_layout(
        title='Warehouse Performance Heatmap',
        height=500,
        margin=dict(l=50, r=50, t=80, b=50),
    )
    
    return fig

def create_bottleneck_chart(df):
    """
    Create a chart showing processing bottlenecks
    """
    if df.empty:
        return go.Figure()
    
    # Define processing stages (example based on processing time)
    df['processing_time_numeric'] = pd.to_numeric(df['processing_time'], errors='coerce')
    process_stages = {
        'Order Receipt': [0, 1],
        'Picking': [1, 3],
        'Packing': [3, 6],
        'Quality Check': [6, 10],
        'Shipping': [10, float('inf')]
    }
    
    # Create stage data
    stage_data = []
    for stage, (min_time, max_time) in process_stages.items():
        stage_count = ((df['processing_time_numeric'] >= min_time) & 
                      (df['processing_time_numeric'] < max_time)).sum()
        avg_time = df[(df['processing_time_numeric'] >= min_time) & 
                      (df['processing_time_numeric'] < max_time)]['processing_time_numeric'].mean()
        stage_data.append({
            'stage': stage,
            'count': stage_count,
            'avg_time': avg_time if not pd.isna(avg_time) else 0
        })
    
    stage_df = pd.DataFrame(stage_data)
    
    # Create two subplots
    fig = go.Figure()
    
    # Add bar chart for count
    fig.add_trace(go.Bar(
        x=stage_df['stage'],
        y=stage_df['count'],
        name='Order Count',
        marker_color='lightblue'
    ))
    
    # Add line chart for average time
    fig.add_trace(go.Scatter(
        x=stage_df['stage'],
        y=stage_df['avg_time'],
        name='Avg Processing Time (hrs)',
        mode='lines+markers',
        marker=dict(size=10, color='red'),
        yaxis='y2'
    ))
    
    # Update layout
    fig.update_layout(
        title='Process Bottleneck Analysis',
        xaxis=dict(title='Processing Stage'),
        yaxis=dict(
            title='Order Count',
            side='left'
        ),
        yaxis2=dict(
            title='Average Processing Time (hrs)',
            side='right',
            overlaying='y',
            showgrid=False
        ),
        legend=dict(x=0.01, y=0.99),
        height=500,
    )
    
    return fig

def create_performance_comparison(warehouse_performance):
    """
    Create a chart comparing performance across warehouses
    """
    if warehouse_performance.empty:
        return go.Figure()
    
    # Create a bar chart comparing warehouses
    fig = px.bar(
        warehouse_performance,
        x='warehouse_name',
        y=['avg_processing_time', 'delay_rate', 'fulfillment_rate'],
        barmode='group',
        title='Warehouse Performance Comparison',
        labels={
            'value': 'Metric Value',
            'warehouse_name': 'Warehouse',
            'variable': 'Metric'
        },
        color_discrete_map={
            'avg_processing_time': '#FF9999',
            'delay_rate': '#FFCC99',
            'fulfillment_rate': '#99CC99'
        }
    )
    
    # Update layout
    fig.update_layout(
        height=500,
        legend=dict(
            title='Metrics',
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )
    
    return fig

def create_time_series_chart(df):
    """
    Create a time series chart showing performance over time
    """
    if df.empty:
        return go.Figure()
    
    # Ensure date formats
    if df['order_date'].dtype != 'datetime64[ns]':
        df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
    
    # Create date column
    df['date'] = df['order_date'].dt.date
    
    # Ensure processing_time is numeric
    df['processing_time_numeric'] = pd.to_numeric(df['processing_time'], errors='coerce')
    
    # Group by date
    time_data = df.groupby('date').agg({
        'processing_time_numeric': 'mean',
        'order_id': 'count'
    }).reset_index()
    
    time_data.columns = ['date', 'avg_processing_time', 'order_count']
    
    # Create figure with secondary y-axis
    fig = go.Figure()
    
    # Add traces
    fig.add_trace(
        go.Scatter(
            x=time_data['date'],
            y=time_data['avg_processing_time'],
            name="Avg Processing Time (hrs)",
            line=dict(color="red", width=2)
        )
    )
    
    fig.add_trace(
        go.Bar(
            x=time_data['date'],
            y=time_data['order_count'],
            name="Order Count",
            marker_color="lightblue",
            opacity=0.7,
            yaxis="y2"
        )
    )
    
    # Create layout with secondary y-axis
    fig.update_layout(
        title="Performance Trends Over Time",
        xaxis=dict(
            title="Date",
            tickangle=45,
            tickformat="%Y-%m-%d"
        ),
        yaxis=dict(
            title=dict(
                text="Avg Processing Time (hrs)",
                font=dict(color="red")
            ),
            tickfont=dict(color="red")
        ),
        yaxis2=dict(
            title=dict(
                text="Order Count",
                font=dict(color="blue")
            ),
            tickfont=dict(color="blue"),
            anchor="x",
            overlaying="y",
            side="right"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=500
    )
    
    return fig
