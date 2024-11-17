from flask import Blueprint, render_template, jsonify, request, current_app
from src.model_predictor import ModelPredictor
from src.transaction_simulator import TransactionSimulator
from src.rules_engine import RulesEngine
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fraud_detection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create blueprint
main_bp = Blueprint('main', __name__)

# Initialize components
model_predictor = ModelPredictor('models/')
transaction_simulator = TransactionSimulator()
rules_engine = RulesEngine('config/rules_config.yaml')

# In-memory storage
class TransactionStore:
    def __init__(self):
        self.transactions: List[Dict] = []
        self.flagged_transactions: List[Dict] = []
        self.start_time = datetime.now()

    def add_transaction(self, transaction: Dict) -> None:
        """Add a transaction and check if it should be flagged"""
        # Add timestamp if not present
        if 'timestamp' not in transaction:
            transaction['timestamp'] = datetime.now().isoformat()
            
        self.transactions.append(transaction)
        
        # Keep only last 1000 transactions
        if len(self.transactions) > 1000:
            self.transactions = self.transactions[-1000:]
            
        # Check if transaction should be flagged
        if (transaction.get('prediction') == 'fraud' or 
            transaction.get('risk_level') in ['high', 'very_high'] or
            transaction.get('fraud_probability', 0) > 0.7):
            self.flagged_transactions.append(transaction)
            
            # Keep only last 100 flagged transactions
            if len(self.flagged_transactions) > 100:
                self.flagged_transactions = self.flagged_transactions[-100:]

    def get_metrics(self) -> Dict:
        """Calculate current metrics"""
        total = len(self.transactions)
        flagged = len(self.flagged_transactions)
        
        if total == 0:
            return {
                'total_transactions': 0,
                'flagged_transactions': 0,
                'fraud_rate': 0,
                'average_amount': 0,
                'total_amount': 0
            }
            
        total_amount = sum(t.get('Amount', 0) for t in self.transactions)
        
        return {
            'total_transactions': total,
            'flagged_transactions': flagged,
            'fraud_rate': (flagged/total) * 100,
            'average_amount': total_amount/total,
            'total_amount': total_amount
        }

    def get_analytics_data(self) -> Dict:
        """Get analytics data for visualization"""
        if not self.transactions:
            return {
                'amount_distribution': {},
                'risk_distribution': {},
                'hourly_transactions': {},
                'fraud_by_type': {},
                'risk_by_amount': []
            }
            
        df = pd.DataFrame(self.transactions)
        
        # Convert timestamp strings to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return {
            'amount_distribution': df['Amount'].describe().to_dict(),
            'risk_distribution': df.groupby('risk_level').size().to_dict(),
            'hourly_transactions': df.groupby(df['timestamp'].dt.hour).size().to_dict(),
            'fraud_by_type': df[df['prediction'] == 'fraud']['pattern_type'].value_counts().to_dict(),
            'risk_by_amount': df[['Amount', 'fraud_probability']].values.tolist()
        }

    def clear(self) -> None:
        """Reset the store"""
        self.transactions = []
        self.flagged_transactions = []
        self.start_time = datetime.now()

# Initialize store
store = TransactionStore()

# Routes
@main_bp.route('/')
def dashboard():
    """Main dashboard view"""
    return render_template('dashboard.html')

@main_bp.route('/analytics')
def analytics():
    """Analytics view"""
    return render_template('analytics.html')

@main_bp.route('/flagged')
def flagged_reviews():
    """Flagged transactions view"""
    return render_template('flagged_reviews.html')

# API Endpoints
@main_bp.route('/api/simulate', methods=['POST'])
def simulate_transaction():
    """Generate and process new transaction"""
    try:
        # Generate transaction with location and customer info
        transaction = transaction_simulator.generate_transaction()
        logger.info(f"Generated transaction: {transaction}")

        # Get ML prediction
        prediction = model_predictor.predict(transaction)
        transaction.update(prediction)
        logger.info(f"Prediction: {prediction}")

        # Apply rules
        rules_result = rules_engine.evaluate_transaction(transaction, prediction)
        transaction.update(rules_result)
        logger.info(f"Rules evaluation: {rules_result}")

        # Store transaction
        store.add_transaction(transaction)

        response_data = {
            'status': 'success',
            'transaction': {
                'transaction_id': transaction['transaction_id'],
                'timestamp': transaction['timestamp'],
                'Time': transaction['Time'],
                'Amount': float(transaction['Amount']),
                'location': transaction['location'],
                'pattern_type': transaction['pattern_type'],
                'risk_level': transaction['risk_level'],
                'customer_risk_level': transaction['customer_risk_level'],
                'fraud_probability': float(prediction.get('fraud_probability', 0)),
                'prediction': prediction.get('prediction', 'unknown')
            }
        }

        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Error in simulation: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e),
            'error_type': type(e).__name__
        }), 400

@main_bp.route('/api/transactions/latest')
def get_latest_transactions():
    """Get latest transactions"""
    try:
        return jsonify({
            'status': 'success',
            'transactions': store.transactions[-100:],  # Last 100 transactions
            'flagged': store.flagged_transactions[-20:]  # Last 20 flagged transactions
        })
    except Exception as e:
        logger.error(f"Error getting transactions: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@main_bp.route('/api/metrics')
def get_metrics():
    """Get current metrics"""
    try:
        return jsonify(store.get_metrics())
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@main_bp.route('/api/analytics/data')
def get_analytics_data():
    """Get analytics data"""
    try:
        return jsonify(store.get_analytics_data())
    except Exception as e:
        logger.error(f"Error getting analytics data: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@main_bp.route('/api/flagged/data')
def get_flagged_data():
    """Get flagged transactions"""
    try:
        return jsonify({
            'status': 'success',
            'transactions': store.flagged_transactions
        })
    except Exception as e:
        logger.error(f"Error getting flagged transactions: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@main_bp.route('/api/flagged/review', methods=['POST'])
def review_flagged_transaction():
    """Review a flagged transaction"""
    try:
        data = request.json
        transaction_id = data.get('transaction_id')
        review_status = data.get('status')
        
        # Update transaction status
        for transaction in store.flagged_transactions:
            if transaction['transaction_id'] == transaction_id:
                transaction['review_status'] = review_status
                transaction['reviewed_at'] = datetime.now().isoformat()
                transaction['reviewed_by'] = data.get('user', 'admin')
                return jsonify({'status': 'success'})
        
        return jsonify({
            'status': 'error',
            'message': 'Transaction not found'
        }), 404
    except Exception as e:
        logger.error(f"Error reviewing transaction: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@main_bp.route('/api/reset', methods=['POST'])
def reset_simulation():
    """Reset the simulation"""
    try:
        store.clear()
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error resetting simulation: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@main_bp.route('/api/status')
def get_system_status():
    """Get system status"""
    try:
        return jsonify({
            'status': 'success',
            'uptime': (datetime.now() - store.start_time).total_seconds(),
            'total_transactions': len(store.transactions),
            'flagged_transactions': len(store.flagged_transactions),
            'last_transaction': store.transactions[-1]['timestamp'] if store.transactions else None
        })
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400