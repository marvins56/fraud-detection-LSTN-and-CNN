# import random
# import time
# from datetime import datetime
# import numpy as np
# from typing import Dict, Any, List  # Add this import for type hints
# import uuid

# class TransactionSimulator:
#     def __init__(self):
#         self.api_url = 'http://localhost:5000/predict'
        
#         # Define transaction patterns
#         self.transaction_patterns = {
#             'normal_low': {
#                 'amount_range': (10, 100),
#                 'frequency': 0.4,
#                 'risk_level': 'low'
#             },
#             'normal_high': {
#                 'amount_range': (100, 1000),
#                 'frequency': 0.3,
#                 'risk_level': 'low'
#             },
#             'high_value': {
#                 'amount_range': (1000, 5000),
#                 'frequency': 0.2,
#                 'risk_level': 'medium'
#             },
#             'suspicious': {
#                 'amount_range': (500, 10000),
#                 'frequency': 0.08,
#                 'risk_level': 'high'
#             },
#             'fraudulent': {
#                 'amount_range': (1000, 50000),
#                 'frequency': 0.02,
#                 'risk_level': 'very_high'
#             }
#         }
        
#         self.customers = self._generate_customers(1000)
#         self.locations = self._generate_locations()
    
#     def _generate_customers(self, num_customers: int) -> Dict[str, Dict[str, Any]]:
#         """Generate a pool of customers with different profiles"""
#         customers = {}
#         for _ in range(num_customers):
#             customer_id = str(uuid.uuid4())
#             customers[customer_id] = {
#                 'risk_level': random.choices(
#                     ['low', 'medium', 'high'],
#                     weights=[0.8, 0.15, 0.05]
#                 )[0],
#                 'usual_locations': random.sample(self._generate_locations(), 3),
#                 'usual_transaction_range': random.choice([
#                     (10, 100),
#                     (100, 500),
#                     (500, 1000),
#                     (1000, 5000)
#                 ])
#             }
#         return customers
    
#     def _generate_locations(self) -> List[str]:
#         """Generate a list of transaction locations"""
#         return [
#             'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix',
#             'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose'
#         ]
    
#     def generate_transaction(self) -> Dict[str, Any]:
#         """Generate a single transaction"""
#         # Select pattern
#         pattern_type = random.choices(
#             list(self.transaction_patterns.keys()),
#             weights=[p['frequency'] for p in self.transaction_patterns.values()]
#         )[0]
#         pattern = self.transaction_patterns[pattern_type]
        
#         # Select customer
#         customer_id = random.choice(list(self.customers.keys()))
#         customer = self.customers[customer_id]
        
#         # Generate amount based on pattern and customer profile
#         amount = round(random.uniform(*pattern['amount_range']), 2)
        
#         # Select location
#         if pattern['risk_level'] in ['high', 'very_high']:
#             location = random.choice(self.locations)  # Any location
#         else:
#             location = random.choice(customer['usual_locations'])
        
#         # Generate transaction
#         transaction = {
#             'transaction_id': str(uuid.uuid4()),
#             'customer_id': customer_id,
#             'timestamp': datetime.now(),
#             'Time': time.time(),
#             'Amount': amount,
#             'location': location,
#             'pattern_type': pattern_type,
#             'risk_level': pattern['risk_level']
#         }
        
#         return transaction

#     def generate_transactions_stream(self, delay_range=(1, 3)):
#         """Generate a continuous stream of transactions"""
#         try:
#             while True:
#                 transaction = self.generate_transaction()
#                 print(f"Generated transaction: {transaction}")
                
#                 # Random delay between transactions
#                 delay = random.uniform(*delay_range)
#                 time.sleep(delay)
                
#         except KeyboardInterrupt:
#             print("Transaction generation stopped")

# import random
# import time
# import asyncio
# import requests
# from datetime import datetime
# import numpy as np
# from typing import Dict, Any, List
# import uuid

# class TransactionSimulator:
#     def __init__(self):
#         self.transaction_patterns = {
#             'normal_low': {
#                 'amount_range': (10, 100),
#                 'frequency': 0.4,
#                 'risk_level': 'low'
#             },
#             'normal_high': {
#                 'amount_range': (100, 1000),
#                 'frequency': 0.3,
#                 'risk_level': 'low'
#             },
#             'high_value': {
#                 'amount_range': (1000, 5000),
#                 'frequency': 0.2,
#                 'risk_level': 'medium'
#             },
#             'suspicious': {
#                 'amount_range': (500, 10000),
#                 'frequency': 0.08,
#                 'risk_level': 'high'
#             },
#             'fraudulent': {
#                 'amount_range': (1000, 50000),
#                 'frequency': 0.02,
#                 'risk_level': 'very_high'
#             }
#         }

#     def generate_transaction(self) -> Dict[str, Any]:
#         """Generate a single transaction"""
#         # Select pattern
#         pattern_type = random.choices(
#             list(self.transaction_patterns.keys()),
#             weights=[p['frequency'] for p in self.transaction_patterns.values()]
#         )[0]
#         pattern = self.transaction_patterns[pattern_type]
        
#         # Generate amount based on pattern
#         amount = round(random.uniform(*pattern['amount_range']), 2)
        
#         # Generate transaction
#         transaction = {
#             'transaction_id': str(uuid.uuid4()),
#             'timestamp': datetime.now().isoformat(),
#             'Time': time.time(),
#             'Amount': amount,
#             'pattern_type': pattern_type,
#             'risk_level': pattern['risk_level']
#         }
        
#         return transaction
    
    
    
    

#     async def simulate_transactions(self, delay_range=(1, 3)):
#         """Generate and send transactions continuously"""
#         print("Starting transaction simulation...")
        
#         while True:
#             try:
#                 # Generate transaction
#                 transaction = self.generate_transaction()
                
#                 # Print transaction details
#                 print("\nGenerated Transaction:")
#                 print(f"ID: {transaction['transaction_id']}")
#                 print(f"Amount: ${transaction['Amount']:.2f}")
#                 print(f"Type: {transaction['pattern_type']}")
#                 print(f"Risk Level: {transaction['risk_level']}")
                
#                 # Send to Streamlit (using session state)
#                 try:
#                     requests.post('http://localhost:8501/update_data', 
#                                 json=transaction,
#                                 timeout=1)
#                 except:
#                     pass  # Ignore connection errors
                
#                 # Random delay between transactions
#                 delay = random.uniform(*delay_range)
#                 await asyncio.sleep(delay)
                
#             except Exception as e:
#                 print(f"Error generating transaction: {str(e)}")
#                 await asyncio.sleep(1)

# def main():
#     simulator = TransactionSimulator()
#     print("Transaction simulator started")
    
#     try:
#         asyncio.run(simulator.simulate_transactions(delay_range=(1, 3)))
#     except KeyboardInterrupt:
#         print("\nSimulation stopped by user")
#     except Exception as e:
#         print(f"\nError in simulator: {str(e)}")

# if __name__ == "__main__":
#     main()

import random
import time
import asyncio
import requests
from datetime import datetime
import numpy as np
from typing import Dict, Any, List
import uuid
import logging

class TransactionSimulator:
    def __init__(self):
        # Setup logging
        self.setup_logging()
        
        # Define transaction patterns
        self.transaction_patterns = {
            'normal_low': {
                'amount_range': (10, 100),
                'frequency': 0.4,
                'risk_level': 'low'
            },
            'normal_high': {
                'amount_range': (100, 1000),
                'frequency': 0.3,
                'risk_level': 'low'
            },
            'high_value': {
                'amount_range': (1000, 5000),
                'frequency': 0.2,
                'risk_level': 'medium'
            },
            'suspicious': {
                'amount_range': (500, 10000),
                'frequency': 0.08,
                'risk_level': 'high'
            },
            'fraudulent': {
                'amount_range': (1000, 50000),
                'frequency': 0.02,
                'risk_level': 'very_high'
            }
        }

        # Generate customer profiles and locations
        self.customers = self._generate_customers(1000)
        self.locations = self._generate_locations()

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('transaction_simulator.log')
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _generate_customers(self, num_customers: int) -> Dict[str, Dict[str, Any]]:
        """Generate a pool of customers with different profiles"""
        customers = {}
        for _ in range(num_customers):
            customer_id = str(uuid.uuid4())
            customers[customer_id] = {
                'risk_level': random.choices(
                    ['low', 'medium', 'high'],
                    weights=[0.8, 0.15, 0.05]
                )[0],
                'usual_locations': random.sample(self._generate_locations(), 3),
                'usual_transaction_range': random.choice([
                    (10, 100),
                    (100, 500),
                    (500, 1000),
                    (1000, 5000)
                ])
            }
        return customers
    
    def _generate_locations(self) -> List[str]:
        """Generate a list of transaction locations"""
        return [
            'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix',
            'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose'
        ]

    def generate_transaction(self) -> Dict[str, Any]:
        """Generate a single transaction"""
        try:
            # Select pattern
            pattern_type = random.choices(
                list(self.transaction_patterns.keys()),
                weights=[p['frequency'] for p in self.transaction_patterns.values()]
            )[0]
            pattern = self.transaction_patterns[pattern_type]
            
            # Select customer
            customer_id = random.choice(list(self.customers.keys()))
            customer = self.customers[customer_id]
            
            # Generate amount based on pattern and customer profile
            amount = round(random.uniform(*pattern['amount_range']), 2)
            
            # Select location
            if pattern['risk_level'] in ['high', 'very_high']:
                location = random.choice(self.locations)  # Any location
            else:
                location = random.choice(customer['usual_locations'])
            
            # Generate timestamps
            current_time = datetime.now()
            
            # Generate transaction
            transaction = {
                'transaction_id': str(uuid.uuid4()),
                'customer_id': customer_id,
                'timestamp': current_time.isoformat(),  # Store as ISO format string
                'Time': time.time(),
                'Amount': amount,
                'location': location,
                'pattern_type': pattern_type,
                'risk_level': pattern['risk_level'],
                'customer_risk_level': customer['risk_level']
            }
            
            self.logger.info(f"Generated transaction: {transaction}")
            return transaction
            
        except Exception as e:
            self.logger.error(f"Error generating transaction: {str(e)}")
            raise

    def format_transaction_for_display(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Format transaction for display/storage"""
        display_transaction = transaction.copy()
        
        # Convert timestamp to datetime if it's a string
        if isinstance(display_transaction.get('timestamp'), str):
            display_transaction['timestamp'] = datetime.fromisoformat(display_transaction['timestamp'])
        
        return display_transaction

    async def simulate_transactions(self, delay_range=(1, 3)):
        """Generate and send transactions continuously"""
        self.logger.info("Starting transaction simulation...")
        
        while True:
            try:
                # Generate transaction
                transaction = self.generate_transaction()
                display_transaction = self.format_transaction_for_display(transaction)
                
                # Print transaction details
                self.logger.info("\nGenerated Transaction:")
                self.logger.info(f"ID: {display_transaction['transaction_id']}")
                self.logger.info(f"Amount: ${display_transaction['Amount']:.2f}")
                self.logger.info(f"Type: {display_transaction['pattern_type']}")
                self.logger.info(f"Risk Level: {display_transaction['risk_level']}")
                self.logger.info(f"Location: {display_transaction['location']}")
                self.logger.info(f"Customer Risk Level: {display_transaction['customer_risk_level']}")
                
                # Try to send to Streamlit
                try:
                    requests.post(
                        'http://localhost:8501/update_data', 
                        json=transaction,
                        timeout=1
                    )
                except:
                    pass  # Ignore connection errors
                
                # Random delay between transactions
                delay = random.uniform(*delay_range)
                await asyncio.sleep(delay)
                
            except Exception as e:
                self.logger.error(f"Error in simulation: {str(e)}")
                await asyncio.sleep(1)

def main():
    simulator = TransactionSimulator()
    print("Transaction simulator started")
    
    try:
        asyncio.run(simulator.simulate_transactions(delay_range=(1, 3)))
    except KeyboardInterrupt:
        print("\nSimulation stopped by user")
    except Exception as e:
        print(f"\nError in simulator: {str(e)}")

if __name__ == "__main__":
    main()