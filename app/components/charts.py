import altair as alt
import pandas as pd
from typing import Dict, Any

def create_time_series_chart(data: pd.DataFrame, 
                           y_field: str,
                           title: str,
                           color_field: str = None) -> alt.Chart:
    """Create a time series chart"""
    chart = alt.Chart(data).mark_line().encode(
        x='timestamp:T',
        y=f'{y_field}:Q',
        tooltip=['timestamp:T', f'{y_field}:Q']
    ).properties(
        title=title,
        height=300
    ).interactive()
    
    if color_field:
        chart = chart.encode(color=f'{color_field}:N')
    
    return chart

def create_distribution_chart(data: pd.DataFrame,
                            field: str,
                            title: str) -> alt.Chart:
    """Create a distribution chart"""
    return alt.Chart(data).mark_bar().encode(
        x=alt.X(f'{field}:Q', bin=True),
        y='count()',
        tooltip=['count()']
    ).properties(
        title=title,
        height=300
    ).interactive()

def create_scatter_plot(data: pd.DataFrame,
                       x_field: str,
                       y_field: str,
                       color_field: str,
                       title: str) -> alt.Chart:
    """Create a scatter plot"""
    return alt.Chart(data).mark_circle().encode(
        x=f'{x_field}:Q',
        y=f'{y_field}:Q',
        color=f'{color_field}:N',
        tooltip=[x_field, y_field, color_field]
    ).properties(
        title=title,
        height=300
    ).interactive()