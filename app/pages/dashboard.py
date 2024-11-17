import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
from src.utils import calculate_transaction_metrics, get_time_window_transactions

def render_dashboard(transactions_df: pd.DataFrame):
    st.title("Transaction Monitoring Dashboard")
    
    # Time window selector
    time_window = st.selectbox(
        "Time Window",
        options=[15, 30, 60, 360, 720],
        format_func=lambda x: f"Last {x} minutes",
        index=2
    )
    
    # Get recent transactions
    recent_transactions = get_time_window_transactions(transactions_df, time_window)
    
    # Display metrics
    metrics = calculate_transaction_metrics(recent_transactions)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Transaction Count", metrics['transaction_count'])
    with col2:
        st.metric("Total Amount", f"${metrics['total_amount']:,.2f}")
    with col3:
        st.metric("Average Amount", f"${metrics['avg_amount']:,.2f}")
    with col4:
        st.metric("Fraud Rate", f"{metrics['fraud_rate']:.2f}%")
    
    # Display charts
    display_transaction_charts(recent_transactions)
    
    # Display recent transactions
    display_recent_transactions(recent_transactions)

def display_transaction_charts(df: pd.DataFrame):
    if df.empty:
        st.warning("No transactions in selected time window")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Transaction amounts over time
        chart1 = alt.Chart(df).mark_circle().encode(
            x='timestamp:T',
            y='Amount:Q',
            color='final_decision:N',
            size='risk_score:Q',
            tooltip=['transaction_id', 'Amount', 'risk_score', 'final_decision']
        ).properties(
            title='Transaction Amounts Over Time',
            height=300
        ).interactive()
        
        st.altair_chart(chart1, use_container_width=True)
    
    with col2:
        # Risk score distribution
        chart2 = alt.Chart(df).mark_bar().encode(
            x=alt.X('risk_score:Q', bin=True),
            y='count()',
            color='final_decision:N'
        ).properties(
            title='Risk Score Distribution',
            height=300
        ).interactive()
        
        st.altair_chart(chart2, use_container_width=True)

def display_recent_transactions(df: pd.DataFrame):
    st.subheader("Recent Transactions")
    
    if df.empty:
        st.info("No transactions to display")
        return
    
    # Display as table
    st.dataframe(
        df.sort_values('timestamp', ascending=False)
        .head(10)
        [['timestamp', 'Amount', 'risk_score', 'final_decision', 'transaction_id']]
    )