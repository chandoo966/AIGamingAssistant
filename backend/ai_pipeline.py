import logging
from typing import Dict, List, Any
from .suggestion_models import SUGGESTIONS

class AISuggestionPipeline:
    def __init__(self):
        self.logger = logging.getLogger('AISuggestionPipeline')
        self.suggestions = SUGGESTIONS
        
    def get_suggestions(self, state: Dict[str, Any], game: str = 'valorant') -> List[Dict[str, Any]]:
        """Get suggestions based on current game state"""
        try:
            # Get all suggestions for the current game
            game_suggestions = self.suggestions.get(game, [])  # Default to Valorant
            
            # Filter suggestions based on state
            active_suggestions = []
            for suggestion in game_suggestions:
                if self._check_conditions(suggestion, state):
                    active_suggestions.append(suggestion)
                    
            # Sort by priority
            active_suggestions.sort(key=lambda x: x['priority'])
            
            # Return top 3 suggestions
            return active_suggestions[:3]
            
        except Exception as e:
            self.logger.error(f"Error getting suggestions: {e}")
            return []
            
    def _check_conditions(self, suggestion: Dict[str, Any], state: Dict[str, Any]) -> bool:
        """Check if suggestion conditions are met, including nested dicts for abilities, etc."""
        try:
            conditions = suggestion.get('conditions', {})
            for key, value in conditions.items():
                if key not in state:
                    self.logger.debug(f"Suggestion {suggestion.get('id')} not matched: key '{key}' missing in state.")
                    return False
                # Special handling for nested dicts (e.g., abilities)
                if isinstance(value, dict) and isinstance(state[key], dict):
                    for subkey, subval in value.items():
                        if subkey not in state[key] or state[key][subkey] != subval:
                            self.logger.debug(f"Suggestion {suggestion.get('id')} not matched: abilities subkey '{subkey}' expected {subval}, got {state[key].get(subkey)}.")
                            return False
                else:
                    if state[key] != value:
                        self.logger.debug(f"Suggestion {suggestion.get('id')} not matched: key '{key}' expected {value}, got {state[key]}.")
                        return False
            self.logger.debug(f"Suggestion {suggestion.get('id')} matched for state.")
            return True
        except Exception as e:
            self.logger.error(f"Error checking conditions: {e}")
            return False