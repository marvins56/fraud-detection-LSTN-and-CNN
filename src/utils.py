import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any

def calculate_transaction_metrics(transactions_df: pd.DataFrame) -> Dict[str, float]:
    """Calculate key transaction metrics"""
    if transactions_df.empty:
        return {
            'total_amount': 0,
            'avg_amount': 0,
            'fraud_rate': 0,
            'transaction_count': 0,
            'flagged_count': 0
        }
    
    metrics = {
        'total_amount': transactions_df['Amount'].sum(),
        'avg_amount': transactions_df['Amount'].mean(),
        'transaction_count': len(transactions_df),
        'flagged_count': len(transactions_df[transactions_df['final_decision'] == 'flagged']),
    }
    
    metrics['fraud_rate'] = (metrics['flagged_count'] / metrics['transaction_count']) * 100
    
    return metrics

def get_time_window_transactions(transactions_df: pd.DataFrame, 
                               minutes: int = 60) -> pd.DataFrame:
    """Get transactions within recent time window"""
    if transactions_df.empty:
        return transactions_df
        
    cutoff_time = datetime.now() - timedelta(minutes=minutes)
    return transactions_df[transactions_df['timestamp'] > cutoff_time]

def format_currency(amount: float) -> str:
    """Format amount as currency string"""
    return f"${amount:,.2f}"

def calculate_risk_score(transaction: Dict[str, Any], 
                        ml_probability: float, 
                        rule_flags: List[Dict]) -> float:
    """Calculate overall risk score based on ML prediction and rules"""
    base_score = ml_probability * 100  # Convert to 0-100 scale
    
    # Add points for each triggered rule
    rule_points = sum(10 for _ in rule_flags)
    
    # Add points for amount-based risk
    amount = transaction['Amount']
    if amount > 10000:
        rule_points += 20
    elif amount > 5000:
        rule_points += 10
    elif amount > 1000:
        rule_points += 5
    
    # Combine scores
    final_score = (base_score + rule_points) / 2
    
    return min(final_score, 100)  # Cap at 100