from abc import ABC, abstractmethod
import numpy as np
from typing import Dict, Any, List, Optional
import torch
import torch.nn as nn
import logging

class BaseGameModel(ABC):
    """Base class for all game-specific ML models"""
    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize the base model"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Model should be initialized by child class before calling super().__init__
        if not hasattr(self, 'model'):
            raise ValueError("Child class must initialize self.model before calling super().__init__")
            
        if model_path:
            self.load_model(model_path)
            
    @abstractmethod
    def preprocess_state(self, state: Dict[str, Any]) -> torch.Tensor:
        """Convert game state to model input tensor"""
        pass
        
    @abstractmethod
    def postprocess_output(self, output: torch.Tensor) -> Dict[str, Any]:
        """Convert model output to game suggestions"""
        pass
        
    @abstractmethod
    def train(self, training_data: List[Dict[str, Any]], labels: List[Dict[str, Any]]):
        """Train the model on game data"""
        pass
        
    def predict(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Make predictions based on current game state"""
        try:
            # Preprocess input
            input_tensor = self.preprocess_state(state)
            input_tensor = input_tensor.to(self.device)
            
            # Get model prediction
            with torch.no_grad():
                output = self.model(input_tensor)
                
            # Postprocess output
            return self.postprocess_output(output)
            
        except Exception as e:
            self.logger.error(f"Error making prediction: {e}")
            return {}
            
    def save_model(self, path: str):
        """Save model to file"""
        try:
            torch.save({
                'model_state_dict': self.model.state_dict(),
                'model_config': self.model.get_config()
            }, path)
            self.logger.info(f"Model saved to {path}")
        except Exception as e:
            self.logger.error(f"Error saving model: {e}")
            
    def load_model(self, path: str):
        """Load model from file"""
        try:
            checkpoint = torch.load(path, map_location=self.device)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.to(self.device)
            self.model.eval()
            self.logger.info(f"Model loaded from {path}")
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
            
    def evaluate(self, test_data: List[Dict[str, Any]], test_labels: List[Dict[str, Any]]) -> Dict[str, float]:
        """Evaluate model performance"""
        try:
            self.model.eval()
            total_loss = 0
            correct_predictions = 0
            total_predictions = 0
            
            with torch.no_grad():
                for state, label in zip(test_data, test_labels):
                    input_tensor = self.preprocess_state(state)
                    input_tensor = input_tensor.to(self.device)
                    output = self.model(input_tensor)
                    
                    # Calculate metrics based on model type
                    loss = self.calculate_loss(output, label)
                    total_loss += loss.item()
                    
                    # Update accuracy metrics
                    predictions = self.postprocess_output(output)
                    correct_predictions += self.calculate_accuracy(predictions, label)
                    total_predictions += 1
                    
            return {
                'loss': total_loss / len(test_data),
                'accuracy': correct_predictions / total_predictions
            }
            
        except Exception as e:
            self.logger.error(f"Error evaluating model: {e}")
            return {'loss': float('inf'), 'accuracy': 0.0}
            
    @abstractmethod
    def calculate_loss(self, output: torch.Tensor, target: Dict[str, Any]) -> torch.Tensor:
        """Calculate loss between model output and target"""
        pass
        
    @abstractmethod
    def calculate_accuracy(self, predictions: Dict[str, Any], target: Dict[str, Any]) -> float:
        """Calculate accuracy of predictions"""
        pass 