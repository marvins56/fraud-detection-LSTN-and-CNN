import streamlit as st
import pandas as pd
import altair as alt
from src.utils import calculate_transaction_metrics

def render_analytics(transactions_df: pd.DataFrame):
    st.title("Transaction Analytics")
    
    # Time-based analysis
    st.header("Time-based Analysis")
    display_time_analysis(transactions_df)
    
    # Amount distribution
    st.header("Amount Distribution")
    display_amount_analysis(transactions_df)
    
    # Risk analysis
    st.header("Risk Analysis")
    display_risk_analysis(transactions_df)
    
    # Rule trigger analysis
    st.header("Rule Trigger Analysis")
    display_rule_analysis(transactions_df)

def display_time_analysis(df: pd.DataFrame):
    if df.empty:
        st.info("No data available for analysis")
        return
    
    # Transactions per hour
    hourly = df.set_index('timestamp').resample('H').size()
    
    chart = alt.Chart(hourly.reset_index()).mark_line().encode(
        x='timestamp:T',
        y='0:Q',
        tooltip=['timestamp:T', '0:Q']
    ).properties(
        title='Transactions per Hour',
        height=300
    ).interactive()
    
    st.altair_chart(chart, use_container_width=True)

def display_amount_analysis(df: pd.DataFrame):
    if df.empty:
        return
    
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Amount:Q', bin=True),
        y='count()',
        color='final_decision:N'
    ).properties(
        title='Transaction Amount Distribution',
        height=300
    ).interactive()
    
    st.altair_chart(chart, use_container_width=True)

def display_risk_analysis(df: pd.DataFrame):
    if df.empty:
        return
    
    chart = alt.Chart(df).mark_circle().encode(
        x='Amount:Q',
        y='risk_score:Q',
        color='final_decision:N',
        tooltip=['transaction_id', 'Amount', 'risk_score']
    ).properties(
        title='Risk Score vs Amount',
        height=300
    ).interactive()
    
    st.altair_chart(chart, use_container_width=True)

def display_rule_analysis(df: pd.DataFrame):
    if df.empty or 'flags' not in df.columns:
        return
    
    # Extract rule triggers
    rule_counts = pd.DataFrame([
        flag['name']
        for flags in df['flags'].dropna()
        for flag in flags
    ]).value_counts().reset_index()
    
    rule_counts.columns = ['Rule', 'Count']
    
    chart = alt.Chart(rule_counts).mark_bar().encode(
        y='Rule:N',
        x='Count:Q'
    ).properties(
        title='Rule Trigger Frequency',
        height=300
    ).interactive()
    
    st.altair_chart(chart, use_container_width=True)