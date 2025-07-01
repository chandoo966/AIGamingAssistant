import json
import os
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import numpy as np

class GameDataCollector:
    """Utility for collecting and processing game data for ML training"""
    
    def __init__(self, game_name: str, data_dir: str = "ml/data"):
        self.game_name = game_name
        self.data_dir = data_dir
        self.logger = logging.getLogger('GameDataCollector')
        self.current_session = []
        self.session_start = datetime.now()
        self.setup_directories()
        
    def setup_directories(self):
        """Create necessary directories for data storage"""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            os.makedirs(os.path.join(self.data_dir, self.game_name), exist_ok=True)
        except Exception as e:
            self.logger.error(f"Error creating directories: {e}")
            
    def record_state(self, state: Dict[str, Any], action: Optional[Dict[str, Any]] = None):
        """Record a game state and optional action"""
        try:
            record = {
                'timestamp': datetime.now().isoformat(),
                'state': state,
                'action': action
            }
            self.current_session.append(record)
        except Exception as e:
            self.logger.error(f"Error recording state: {e}")
            
    def save_session(self, success: bool = True):
        """Save the current session data"""
        try:
            if not self.current_session:
                return
                
            # Create session filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"session_{timestamp}_{'success' if success else 'failure'}.json"
            filepath = os.path.join(self.data_dir, self.game_name, filename)
            
            # Save session data
            with open(filepath, 'w') as f:
                json.dump({
                    'game': self.game_name,
                    'success': success,
                    'session_start': self.session_start.isoformat(),
                    'session_end': datetime.now().isoformat(),
                    'records': self.current_session
                }, f, indent=2)
                
            self.logger.info(f"Saved session data to {filepath}")
            self.current_session = []
            self.session_start = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Error saving session: {e}")
            
    def load_training_data(self, min_success_rate: float = 0.5) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Load and process training data from saved sessions"""
        try:
            states = []
            labels = []
            
            # Get all session files
            session_dir = os.path.join(self.data_dir, self.game_name)
            session_files = [f for f in os.listdir(session_dir) if f.endswith('.json')]
            
            for session_file in session_files:
                with open(os.path.join(session_dir, session_file), 'r') as f:
                    session_data = json.load(f)
                    
                # Only use successful sessions or those above minimum success rate
                if session_data.get('success', False) or self._calculate_success_rate(session_data) >= min_success_rate:
                    for record in session_data['records']:
                        if record.get('action'):  # Only use records with actions
                            states.append(record['state'])
                            labels.append(record['action'])
                            
            return states, labels
            
        except Exception as e:
            self.logger.error(f"Error loading training data: {e}")
            return [], []
            
    def _calculate_success_rate(self, session_data: Dict[str, Any]) -> float:
        """Calculate success rate for a session"""
        try:
            if not session_data.get('records'):
                return 0.0
                
            # Count successful actions (you can define your own success criteria)
            successful_actions = sum(1 for record in session_data['records']
                                  if record.get('action', {}).get('success', False))
                                  
            return successful_actions / len(session_data['records'])
            
        except Exception as e:
            self.logger.error(f"Error calculating success rate: {e}")
            return 0.0
            
    def preprocess_data(self, states: List[Dict[str, Any]], labels: List[Dict[str, Any]]) -> tuple[np.ndarray, np.ndarray]:
        """Preprocess data for training"""
        try:
            # Convert states to feature vectors
            X = np.array([self._state_to_features(state) for state in states])
            
            # Convert labels to target vectors
            y = np.array([self._label_to_target(label) for label in labels])
            
            return X, y
            
        except Exception as e:
            self.logger.error(f"Error preprocessing data: {e}")
            return np.array([]), np.array([])
            
    def _state_to_features(self, state: Dict[str, Any]) -> np.ndarray:
        """Convert state dictionary to feature vector"""
        features = []
        
        # Add basic state features
        features.extend([
            float(state.get('combat', False)),
            float(state.get('utility_available', False)),
            float(state.get('exposed', False)),
            float(state.get('player_health', 100) / 100.0),  # Normalize health
            float(state.get('player_armor', 0) / 100.0)    # Normalize armor
        ])
        
        # Add one-hot encoded features
        round_time = state.get('round_time', 'mid')
        round_time_encoding = {
            'early': [1, 0, 0],
            'mid': [0, 1, 0],
            'late': [0, 0, 1]
        }
        features.extend(round_time_encoding.get(round_time, [0, 0, 0]))
        
        money_state = state.get('team_money', 'medium')
        money_encoding = {
            'low': [1, 0, 0],
            'medium': [0, 1, 0],
            'high': [0, 0, 1]
        }
        features.extend(money_encoding.get(money_state, [0, 0, 0]))
        
        # Add site control and enemy presence
        features.extend([
            float(state.get('site_control', False)),
            float(state.get('enemy_presence', False))
        ])
        
        return np.array(features)
        
    def _label_to_target(self, label: Dict[str, Any]) -> np.ndarray:
        """Convert label dictionary to target vector"""
        targets = []
        
        # Action target
        action_idx = {
            'aim': 0,
            'utility': 1,
            'position': 2,
            'coordinate': 3,
            'save': 4
        }.get(label.get('action', ''), 0)
        targets.append(action_idx)
        
        # Position target
        targets.extend(label.get('position', [0, 0]))
        
        # Utility target
        utility_idx = {
            'flash': 0,
            'smoke': 1,
            'molly': 2,
            'save': 3
        }.get(label.get('utility', ''), 0)
        targets.append(utility_idx)
        
        # Strategy target
        strategy_idx = {
            'aggressive': 0,
            'defensive': 1,
            'team_push': 2
        }.get(label.get('strategy', ''), 0)
        targets.append(strategy_idx)
        
        return np.array(targets)

    def clear_session(self):
        """Clear current session data"""
        self.current_session = []
        self.session_start = datetime.now()
