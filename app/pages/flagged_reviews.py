import streamlit as st
import pandas as pd
from datetime import datetime

def render_flagged_reviews(flagged_transactions: pd.DataFrame):
    st.title("Flagged Transaction Review")
    
    if flagged_transactions.empty:
        st.info("No flagged transactions to review")
        return
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        min_risk = st.slider("Minimum Risk Score", 0, 100, 50)
    with col2:
        status_filter = st.multiselect(
            "Status",
            options=['pending', 'reviewed', 'cleared', 'confirmed_fraud'],
            default=['pending']
        )
    
    # Filter transactions
    filtered_transactions = flagged_transactions[
        (flagged_transactions['risk_score'] >= min_risk) &
        (flagged_transactions['status'].isin(status_filter))
    ]
    
    # Display transactions for review
    for _, transaction in filtered_transactions.iterrows():
        with st.expander(
            f"Transaction {transaction['transaction_id']} - ${transaction['Amount']:,.2f}",
            expanded=False
        ):
            display_transaction_details(transaction)
            handle_review_actions(transaction)

def display_transaction_details(transaction):
    """Display detailed transaction information"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Transaction Details")
        st.write(f"Amount: ${transaction['Amount']:,.2f}")
        st.write(f"Time: {transaction['timestamp']}")
        st.write(f"Location: {transaction['location']}")
        st.write(f"Risk Score: {transaction['risk_score']:.2f}")
    
    with col2:
        st.write("Risk Factors")
        st.write(f"ML Probability: {transaction['ml_probability']:.2f}")
        if transaction.get('flags'):
            st.write("Triggered Rules:")
            for flag in transaction['flags']:
                st.write(f"- {flag['name']}")

def handle_review_actions(transaction):
    """Handle review actions for a transaction"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Clear Transaction", key=f"clear_{transaction['transaction_id']}"):
            # Update transaction status
            st.success("Transaction marked as cleared")
            
    with col2:
        if st.button("Confirm Fraud", key=f"fraud_{transaction['transaction_id']}"):
            # Update transaction status
            st.error("Transaction marked as fraudulent")
            
    with col3:
        if st.button("Need Investigation", key=f"investigate_{transaction['transaction_id']}"):
            # Update transaction status
            st.warning("Transaction marked for investigation")