from dataclasses import dataclass
from typing import List, Dict, Any
import yaml
from datetime import datetime, timedelta
import pandas as pd

@dataclass
class TransactionRule:
    rule_id: str
    name: str
    description: str
    priority: int
    conditions: Dict[str, Any]

class RulesEngine:
    def __init__(self, config_path: str):
        self.rules = self._load_rules(config_path)
        self.transaction_history = pd.DataFrame()

    def _load_rules(self, config_path: str) -> List[TransactionRule]:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        rules = []
        for rule_config in config['rules']:
            rules.append(TransactionRule(**rule_config))
        return sorted(rules, key=lambda x: x.priority)

    def evaluate_transaction(self, transaction: Dict[str, Any], ml_prediction: Dict[str, float]) -> Dict[str, Any]:
        """Evaluate transaction against all rules and ML prediction"""
        flags = []
        total_risk_score = 0.0

        # Add transaction to history
        transaction_df = pd.DataFrame([transaction])
        # Ensure timestamp column is in datetime format
        transaction_df['timestamp'] = pd.to_datetime(transaction_df['timestamp'], errors='coerce')
        self.transaction_history = pd.concat([self.transaction_history, transaction_df], ignore_index=True)

        # Apply each rule
        for rule in self.rules:
            if self._check_rule_conditions(rule, transaction, ml_prediction):
                flags.append({
                    'rule_id': rule.rule_id,
                    'name': rule.name,
                    'description': rule.description
                })
                total_risk_score += rule.priority

        # Combine ML prediction with rules
        ml_risk_score = ml_prediction['fraud_probability'] * 100
        total_risk_score = (total_risk_score + ml_risk_score) / 2

        return {
            'transaction_id': transaction['transaction_id'],
            'flags': flags,
            'risk_score': total_risk_score,
            'ml_prediction': ml_prediction['prediction'],
            'ml_probability': ml_prediction['fraud_probability'],
            'final_decision': 'flagged' if flags or ml_prediction['prediction'] == 'fraud' else 'approved'
        }

    def _check_rule_conditions(self, rule: TransactionRule, transaction: Dict[str, Any], 
                             ml_prediction: Dict[str, float]) -> bool:
        """Check if transaction meets rule conditions"""
        conditions = rule.conditions

        # Amount threshold check
        if 'amount_threshold' in conditions:
            if transaction['Amount'] > conditions['amount_threshold']:
                return True

        # Frequency check
        if 'frequency_threshold' in conditions:
            recent_transactions = self._get_recent_transactions(
                transaction['customer_id'],
                minutes=conditions['time_window']
            )
            if len(recent_transactions) > conditions['frequency_threshold']:
                return True

        # Location check
        if 'location_risk' in conditions:
            if transaction.get('location') in conditions['high_risk_locations']:
                return True

        # Time check
        if 'time_risk' in conditions:
            hour = datetime.fromtimestamp(transaction['Time']).hour
            if hour in conditions['high_risk_hours']:
                return True

        # ML probability threshold
        if 'ml_probability_threshold' in conditions:
            if ml_prediction['fraud_probability'] > conditions['ml_probability_threshold']:
                return True

        return False

    def _get_recent_transactions(self, customer_id: str, minutes: int) -> pd.DataFrame:
        """Get recent transactions for a customer within time window"""
        # Ensure timestamp column is in datetime format
        self.transaction_history['timestamp'] = pd.to_datetime(self.transaction_history['timestamp'], errors='coerce')
        
        # Drop rows with invalid timestamps
        self.transaction_history.dropna(subset=['timestamp'], inplace=True)
        
        # Filter transactions within the time window
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent = self.transaction_history[
            (self.transaction_history['customer_id'] == customer_id) &
            (self.transaction_history['timestamp'] > cutoff_time)
        ]
        return recent
