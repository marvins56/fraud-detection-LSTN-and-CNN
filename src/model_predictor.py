# src/model_predictor.py
import torch
import joblib
import numpy as np
from typing import Dict, Any
import torch.nn as nn

# Use the exact same model architectures
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        lstm_out, (h_n, c_n) = self.lstm(x)
        out = self.fc(lstm_out[:, -1, :])  # Use the last time-step's hidden state
        return torch.sigmoid(out)

class CNNModel(nn.Module):
    def __init__(self, input_size, output_size):
        super(CNNModel, self).__init__()
        self.conv1 = nn.Conv1d(in_channels=1, out_channels=64, kernel_size=3)
        self.pool = nn.MaxPool1d(kernel_size=2)
        self.fc1 = nn.Linear(64 * ((input_size - 2) // 2), 64)  # Adjust based on pooling
        self.fc2 = nn.Linear(64, output_size)

    def forward(self, x):
        x = self.conv1(x)
        x = self.pool(x)
        x = x.view(x.size(0), -1)  # Flatten the tensor
        x = self.fc1(x)
        x = self.fc2(x)
        return torch.sigmoid(x)

class ModelPredictor:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.load_models()
        
    def load_models(self):
        """Load the saved models and scaler"""
        # Load model parameters
        self.model_params = joblib.load(f'{self.model_path}/model_params.pkl')
        
        # Load LSTM model with full input size
        self.lstm_model = LSTMModel(
            input_size=self.model_params['input_size'],
            hidden_size=self.model_params['hidden_size'],
            output_size=self.model_params['output_size']
        )
        self.lstm_model.load_state_dict(torch.load(f'{self.model_path}/lstm_model.pth'))
        self.lstm_model.eval()
        
        # Load CNN model with full input size
        self.cnn_model = CNNModel(
            input_size=self.model_params['input_size'],
            output_size=self.model_params['output_size']
        )
        self.cnn_model.load_state_dict(torch.load(f'{self.model_path}/cnn_model.pth'))
        self.cnn_model.eval()
        
        # Load scaler
        self.scaler = joblib.load(f'{self.model_path}/scaler.pkl')
    
    def predict(self, transaction: Dict[str, Any]) -> Dict[str, float]:
        """Make prediction for a single transaction"""
        try:
            # Extract Time and Amount
            features = np.array([[
                transaction['Time'],
                transaction['Amount']
            ]])
            
            # Scale features
            scaled_features = self.scaler.transform(features)
            
            # Create full feature vector (matching training data)
            # Initialize with zeros for V1-V28
            full_features = np.zeros((1, 30))  # 30 features: Time, V1-V28, Amount
            full_features[0, 0] = scaled_features[0, 0]  # Time
            full_features[0, -1] = scaled_features[0, 1]  # Amount
            
            # Convert to tensor and add batch dimension
            input_tensor = torch.FloatTensor(full_features).unsqueeze(1)
            
            # Get predictions
            with torch.no_grad():
                lstm_pred = self.lstm_model(input_tensor)
                cnn_pred = self.cnn_model(input_tensor)
                
            # Combine predictions
            final_pred = (lstm_pred.item() + cnn_pred.item()) / 2
            
            return {
                'prediction': 'fraud' if final_pred > 0.5 else 'legitimate',
                'fraud_probability': final_pred
            }
            
        except Exception as e:
            print(f"Error in prediction: {str(e)}")
            return {
                'prediction': 'error',
                'fraud_probability': 0.0
            }