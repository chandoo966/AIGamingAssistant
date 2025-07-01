import os
from dataclasses import dataclass
from typing import Dict, Any
import json

@dataclass
class GameConfig:
    name: str
    window_title: str
    window_class: str
    capture_region: Dict[str, int]  # x, y, width, height
    min_fps: int
    max_fps: int
    suggestion_cooldown: float

# Overlay configuration
OVERLAY_WIDTH = 300
OVERLAY_HEIGHT = 150
OVERLAY_OPACITY = 0.9
OVERLAY_FONT_SIZE = 14
OVERLAY_BACKGROUND_COLOR = "rgba(0, 0, 0, 0.8)"
OVERLAY_TEXT_COLOR = "white"

# Game-specific configurations
GAME_CONFIGS = {
    'valorant': {
        'window_name': 'VALORANT',  # Primary window name
        'window_aliases': ['VALORANT', 'VALORANT  ', 'Valorant', 'Valorant ', 'VALORANT - Riot Games', 'Valorant - Riot Games'],  # Possible window titles
        'screen_regions': {
            # Typical HUD regions for 1920x1080
            'combat': (800, 800, 320, 200),         # Center-bottom
            'utility': (30, 900, 400, 150),         # Bottom-left
            'round_time': (810, 20, 300, 60),       # Top-center
            'team_money': (30, 60, 300, 100),        # Top-left
            'abilities': (800, 950, 320, 80),         # Bottom-center (abilities bar)
            'equipped_gun': (900, 1000, 120, 60),     # Bottom-center right (gun info)
        }
    },
    'csgo': {
        'window_name': 'Counter-Strike: Global Offensive',
        'screen_regions': {
            'combat': (800, 800, 320, 200),         # Center-bottom
            'utility': (30, 900, 400, 150),         # Bottom-left
            'round_time': (810, 20, 300, 60),       # Top-center
            'team_money': (1580, 60, 300, 100)      # Top-right
        }
    },
    'dota2': {
        'window_name': 'Dota 2',
        'screen_regions': {
            'combat': (800, 800, 320, 200),         # Center-bottom
            'utility': (760, 900, 400, 150),        # Bottom-center
            'team_alive': (810, 20, 300, 60),       # Top-center
            'gold': (1580, 60, 300, 100)            # Top-right
        }
    }
}

# Logging configuration
LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': 'game_assistant.log',
            'mode': 'a',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': 'INFO',
            'propagate': True
        }
    }
}

def load_user_config() -> Dict[str, Any]:
    """Load user-specific configuration if it exists"""
    config_path = os.path.join(os.path.expanduser('~'), '.game_assistant', 'config.json')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading user config: {e}")
    return {}
