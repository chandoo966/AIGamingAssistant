import torch
import torch.nn as nn
import torch.nn.functional as F
import logging
from typing import Dict, Any, List
import numpy as np
from .base_model import BaseGameModel
import requests
from PIL import Image
import io

class ValorantModel(nn.Module):
    """Neural network model for Valorant game state analysis"""
    
    def __init__(self, input_size: int, hidden_size: int = 256):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        
        # Feature extraction layers
        self.feature_extractor = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2)
        )
        
        # Action prediction heads
        self.action_head = nn.Linear(hidden_size, 5)  # 5 possible actions
        self.position_head = nn.Linear(hidden_size, 2)  # x, y coordinates
        self.utility_head = nn.Linear(hidden_size, 4)  # 4 utility types
        
        # Strategy prediction
        self.strategy_head = nn.Linear(hidden_size, 3)  # 3 strategy types
        
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        features = self.feature_extractor(x)
        
        return {
            'action': self.action_head(features),
            'position': self.position_head(features),
            'utility': self.utility_head(features),
            'strategy': self.strategy_head(features)
        }
        
    def get_config(self) -> Dict[str, Any]:
        return {
            'input_size': self.input_size,
            'hidden_size': self.hidden_size
        }

class ValorantGameModel(BaseGameModel):
    """Valorant-specific game model implementation with vision AI integration"""
    
    def __init__(self, model_path: str = None):
        self.logger = logging.getLogger('ValorantGameModel')
        self.model = self._create_model()
        super().__init__(model_path)
        self.model.to(self.device)  # Move model to appropriate device
        self.model.eval()  # Set to evaluation mode
        
    def _create_model(self) -> nn.Module:
        """Create the ValorantModel with correct input size and heads"""
        return ValorantModel(input_size=20)

    def predict(self, state: Dict[str, Any], frame: np.ndarray = None) -> Dict[str, Any]:
        """Make predictions based on game state and optionally a frame using a free vision AI API"""
        suggestions = []
        confidence = 0.8
        try:
            state_tensor = self._state_to_tensor(state).to(self.device)
            with torch.no_grad():
                output = self.model(state_tensor)
            # Use postprocess_output to generate suggestions from model output
            result = self.postprocess_output(output, state)
            suggestions = result.get('suggestions', [])
        except Exception as e:
            self.logger.error(f"Error making predictions: {e}")
            suggestions = []
            confidence = 0.0

        # If a frame is provided, use a free vision AI API (e.g., Hugging Face Inference API)
        if frame is not None:
            try:
                img = Image.fromarray(frame)
                buf = io.BytesIO()
                img.save(buf, format='JPEG')
                buf.seek(0)
                response = requests.post(
                    'https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base',
                    headers={'Authorization': 'demo1'},
                    data=buf.getvalue()
                )
                if response.status_code == 200:
                    result = response.json()
                    caption = result[0]['generated_text'] if isinstance(result, list) and 'generated_text' in result[0] else None
                    if caption:
                        suggestions.append({
                            'id': 'vision_ai',
                            'text': f'Vision AI: {caption}',
                            'priority': 1
                        })
                        confidence = 1.0
            except Exception as e:
                self.logger.error(f"Vision AI API error: {e}")

        return {
            'suggestions': suggestions,
            'confidence': confidence
        }
        
    def _state_to_tensor(self, state: Dict[str, Any]) -> torch.Tensor:
        """Convert game state to tensor format with more features"""
        features = [
            1.0 if state.get('combat', False) else 0.0,
            1.0 if state.get('utility_available', False) else 0.0,
            1.0 if state.get('exposed', False) else 0.0,
            1.0 if state.get('team_money', '') == 'low' else 0.0,
            1.0 if state.get('team_money', '') == 'medium' else 0.0,
            1.0 if state.get('team_money', '') == 'high' else 0.0,
            1.0 if state.get('round_time', '') == 'early' else 0.0,
            1.0 if state.get('round_time', '') == 'mid' else 0.0,
            1.0 if state.get('round_time', '') == 'late' else 0.0,
            float(state.get('player_health', 100)) / 100.0,
            float(state.get('player_armor', 0)) / 100.0,
            float(state.get('player_position', [0.0, 0.0])[0]),
            float(state.get('player_position', [0.0, 0.0])[1]),
            float(len(state.get('enemy_positions', []))),
            1.0 if state.get('site_control', False) else 0.0,
            1.0 if state.get('enemy_presence', False) else 0.0,
            1.0 if state.get('teammate_with_smoke', False) else 0.0,
            1.0 if state.get('teammate_with_flash', False) else 0.0,
            1.0 if state.get('teammate_with_healing', False) else 0.0,
            1.0 if state.get('need_coordination', False) else 0.0
        ]
        return torch.tensor(features, dtype=torch.float32)
        
    def _predictions_to_suggestions(self, predictions: torch.Tensor) -> List[Dict[str, Any]]:
        """Convert model predictions to suggestion format, fallback if no confident suggestion"""
        suggestions = []
        if predictions[0] > 0.3:
            suggestions.append({
                'id': 'ml_combat',
                'text': 'AI suggests focusing on combat',
                'priority': 1
            })
        if predictions[1] > 0.3:
            suggestions.append({
                'id': 'ml_utility',
                'text': 'AI suggests using utility',
                'priority': 2
            })
        if predictions[2] > 0.3:
            suggestions.append({
                'id': 'ml_position',
                'text': 'AI suggests repositioning',
                'priority': 3
            })
        if not suggestions:
            suggestions.append({
                'id': 'ml_default',
                'text': 'No strong suggestion, play safe and gather info.',
                'priority': 4
            })
        return suggestions
        
    def preprocess_state(self, state: Dict[str, Any]) -> torch.Tensor:
        """Convert game state to model input tensor"""
        # Extract relevant features from game state
        features = []
        
        # Combat state
        features.append(1.0 if state.get('combat', False) else 0.0)
        
        # Utility availability
        features.append(1.0 if state.get('utility_available', False) else 0.0)
        
        # Round time (one-hot encoded)
        round_time = state.get('round_time', 'mid')
        round_time_encoding = {
            'early': [1, 0, 0],
            'mid': [0, 1, 0],
            'late': [0, 0, 1]
        }
        features.extend(round_time_encoding.get(round_time, [0, 0, 0]))
        
        # Team money state (one-hot encoded)
        money_state = state.get('team_money', 'medium')
        money_encoding = {
            'low': [1, 0, 0],
            'medium': [0, 1, 0],
            'high': [0, 0, 1]
        }
        features.extend(money_encoding.get(money_state, [0, 0, 0]))
        
        # Exposure state
        features.append(1.0 if state.get('exposed', False) else 0.0)
        
        # Convert to tensor
        return torch.FloatTensor(features)
        
    def postprocess_output(self, output: Dict[str, torch.Tensor], state: Dict[str, Any]) -> Dict[str, Any]:
        """Convert model output to game suggestions"""
        suggestions = []
        
        # Process action predictions
        action_probs = F.softmax(output['action'], dim=-1)
        best_action = torch.argmax(action_probs).item()
        action_suggestions = [
            "Focus on aim and recoil control",
            "Use utility to gain advantage",
            "Reposition to better cover",
            "Coordinate with team",
            "Save for next round"
        ]
        if action_probs[best_action] > 0.5:  # Only suggest if confident
            suggestions.append({
                'title': 'Recommended Action',
                'message': action_suggestions[best_action],
                'priority': 1 if best_action in [0, 2] else 2
            })
            
        # Process position suggestions
        position = output['position'].cpu().numpy()
        if state.get('exposed', False):
            suggestions.append({
                'title': 'Position Warning',
                'message': 'Consider moving to a safer position',
                'priority': 1
            })
            
        # Process utility suggestions
        utility_probs = F.softmax(output['utility'], dim=-1)
        best_utility = torch.argmax(utility_probs).item()
        utility_suggestions = [
            "Use flash to peek",
            "Smoke off angles",
            "Use molly to clear corners",
            "Save utility for later"
        ]
        if utility_probs[best_utility] > 0.4 and state.get('utility_available', False):
            suggestions.append({
                'title': 'Utility Suggestion',
                'message': utility_suggestions[best_utility],
                'priority': 2
            })
            
        # Process strategy suggestions
        strategy_probs = F.softmax(output['strategy'], dim=-1)
        best_strategy = torch.argmax(strategy_probs).item()
        strategy_suggestions = [
            "Play aggressively",
            "Play defensively",
            "Coordinate team push"
        ]
        if strategy_probs[best_strategy] > 0.5:
            suggestions.append({
                'title': 'Strategy Suggestion',
                'message': strategy_suggestions[best_strategy],
                'priority': 2
            })
            
        return {'suggestions': suggestions}
        
    def train(self, training_data: List[Dict[str, Any]], labels: List[Dict[str, Any]]):
        """Train the model on game data"""
        self.model.train()
        optimizer = torch.optim.Adam(self.model.parameters())
        
        for epoch in range(100):  # 100 epochs
            total_loss = 0
            for state, label in zip(training_data, labels):
                # Preprocess input
                input_tensor = self.preprocess_state(state)
                input_tensor = input_tensor.to(self.device)
                
                # Forward pass
                output = self.model(input_tensor)
                
                # Calculate loss
                loss = self.calculate_loss(output, label)
                
                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
                
            # Log training progress
            if (epoch + 1) % 10 == 0:
                self.logger.info(f"Epoch {epoch + 1}, Loss: {total_loss / len(training_data):.4f}")
                
    def calculate_loss(self, output: Dict[str, torch.Tensor], target: Dict[str, Any]) -> torch.Tensor:
        """Calculate loss between model output and target"""
        loss = 0
        
        # Action loss
        action_target = torch.tensor(target['action'], device=self.device)
        loss += F.cross_entropy(output['action'], action_target)
        
        # Position loss
        position_target = torch.tensor(target['position'], device=self.device)
        loss += F.mse_loss(output['position'], position_target)
        
        # Utility loss
        utility_target = torch.tensor(target['utility'], device=self.device)
        loss += F.cross_entropy(output['utility'], utility_target)
        
        # Strategy loss
        strategy_target = torch.tensor(target['strategy'], device=self.device)
        loss += F.cross_entropy(output['strategy'], strategy_target)
        
        return loss
        
    def calculate_accuracy(self, predictions: Dict[str, Any], target: Dict[str, Any]) -> float:
        """Calculate accuracy of predictions"""
        correct = 0
        total = 0
        
        # Action accuracy
        if predictions['suggestions'] and target.get('action'):
            correct += 1 if predictions['suggestions'][0]['message'] == target['action'] else 0
            total += 1
            
        # Utility accuracy
        if len(predictions['suggestions']) > 1 and target.get('utility'):
            correct += 1 if predictions['suggestions'][1]['message'] == target['utility'] else 0
            total += 1
            
        return correct / total if total > 0 else 0.0