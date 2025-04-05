import streamlit as st
import pandas as pd
import datetime

def get_date_range(days=30):
    """
    Return a default date range for the dashboard
    """
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=days)
    return start_date, end_date

def filter_data_by_team(df, team_preset):
    """
    Filter data based on team preset
    """
    if team_preset == "All Teams":
        return df
    
    if team_preset == "Brand Team":
        # Filter for brand-related data
        return df[df['team_assignment'].str.contains('Brand', case=False, na=False) | 
                  df['product_category'].str.contains('Premium|Luxury', case=False, na=False)]
    
    elif team_preset == "Performance Team":
        # Filter for operational performance data
        return df[df['team_assignment'].str.contains('Performance|Operations', case=False, na=False)]
    
    elif team_preset == "Social Media Team":
        # Filter for social media promotion-related data
        return df[df['team_assignment'].str.contains('Social|Marketing', case=False, na=False) |
                  df['product_category'].str.contains('Featured|Campaign', case=False, na=False)]
    
    # Default case - return original dataframe
    return df

def format_metric(value, metric_type):
    """
    Format metrics for display
    """
    if metric_type == "time":
        return f"{value:.2f} hrs"
    elif metric_type == "percentage":
        return f"{value:.1f}%"
    elif metric_type == "count":
        return f"{int(value)}"
    else:
        return f"{value}"

def generate_recommendations(metrics, team_preset):
    """
    Generate recommendations based on metrics and team preset
    """
    recommendations = []
    
    # General recommendations based on metrics
    if metrics.get('avg_handling_time', 0) > 24:
        recommendations.append("⚠️ Handling times are above target. Review warehouse processing workflows.")
    
    if metrics.get('delay_percentage', 0) > 15:
        recommendations.append("⚠️ Delay rates are concerning. Investigate shipping partners and internal processes.")
    
    if metrics.get('fulfillment_rate', 0) < 90:
        recommendations.append("⚠️ Fulfillment rates are below target. Address inventory management.")
    
    # Team specific recommendations
    if team_preset == "Brand Team":
        recommendations.append("Focus on premium product lines which currently have higher processing times.")
        recommendations.append("Consider dedicated handling for high-value items to maintain brand reputation.")
    
    elif team_preset == "Performance Team":
        recommendations.append("Implement cross-training to reduce bottlenecks in the packaging stage.")
        recommendations.append("Review staff allocation during peak hours based on the time analysis.")
    
    elif team_preset == "Social Media Team":
        recommendations.append("Coordinate warehouse staffing with upcoming social media campaigns.")
        recommendations.append("Pre-stock frequently promoted items to reduce processing time during campaign periods.")
    
    return recommendations

def get_slowest_warehouses(warehouse_performance, n=3):
    """
    Return the n slowest warehouses based on processing time
    """
    if warehouse_performance.empty:
        return pd.DataFrame()
    
    return warehouse_performance.sort_values('avg_processing_time', ascending=False).head(n)
