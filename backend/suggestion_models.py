from typing import Dict, List, Any

"""Game-specific suggestions and their conditions"""

# Dictionary of suggestions for each game
SUGGESTIONS = {
    'valorant': [
        {
            'id': 'combat_utility',
            'text': 'Use utility to gain advantage in combat',
            'priority': 1,
            'conditions': {
                'combat': True,
                'utility_available': True,
                'close_range': True
            }
        },
        {
            'id': 'exposed_warning',
            'text': 'You are exposed! Find cover quickly',
            'priority': 2,
            'conditions': {
                'exposed': True
            }
        },
        {
            'id': 'save_money',
            'text': 'Consider saving money for next round',
            'priority': 3,
            'conditions': {
                'team_money': 'low',
                'round_time': 'late'
            }
        },
        {
            'id': 'use_ultimate',
            'text': 'Use your ultimate ability to gain an advantage',
            'priority': 1,
            'conditions': {
                'ultimate_available': True,
                'combat': True
            }
        },
        {
            'id': 'rotate_site',
            'text': 'Rotate to another site to surprise the enemy',
            'priority': 2,
            'conditions': {
                'site_control': False,
                'enemy_presence': True
            }
        },
        {
            'id': 'plant_spike',
            'text': 'Plant the spike to secure the round',
            'priority': 1,
            'conditions': {
                'site_control': True,
                'spike_available': True,
                'safe_to_plant': True
            }
        },
        {
            'id': 'defend_spike',
            'text': 'Defend the spike to win the round',
            'priority': 1,
            'conditions': {
                'spike_planted': True,
                'enemy_presence': True
            }
        },
        {
            'id': 'request_smoke',
            'text': 'Request a smoke from a teammate to block vision',
            'priority': 2,
            'conditions': {
                'need_smoke': True,
                'teammate_with_smoke': True
            }
        },
        {
            'id': 'request_flash',
            'text': 'Request a flash from a teammate to blind the enemy',
            'priority': 2,
            'conditions': {
                'need_flash': True,
                'teammate_with_flash': True
            }
        },
        {
            'id': 'request_healing',
            'text': 'Request healing from a teammate to stay alive',
            'priority': 1,
            'conditions': {
                'low_health': True,
                'teammate_with_healing': True
            }
        },
        {
            'id': 'check_corners',
            'text': 'Check your corners before entering a new area',
            'priority': 3,
            'conditions': {
                'entering_new_area': True
            }
        },
        {
            'id': 'communicate_team',
            'text': 'Communicate with your team to coordinate attacks and defenses',
            'priority': 2,
            'conditions': {
                'need_coordination': True
            }
        },
        {
            'id': 'use_ability_q',
            'text': 'Use your Q ability for tactical advantage',
            'priority': 1,
            'conditions': {
                'abilities': {'Q': True},
                'combat': True
            }
        },
        {
            'id': 'use_ability_e',
            'text': 'Use your E ability to reposition or gather info',
            'priority': 2,
            'conditions': {
                'abilities': {'E': True},
                'combat': True
            }
        },
        {
            'id': 'switch_to_rifle',
            'text': 'Switch to a rifle for better firepower',
            'priority': 2,
            'conditions': {
                'equipped_gun': 'Classic',
                'combat': True
            }
        },
        {
            'id': 'default_tip',
            'text': 'Play smart and communicate with your team!',
            'priority': 99,
            'conditions': {}
        }
    ],
    'csgo': [
        {
            'id': 'combat_utility',
            'text': 'Use utility to gain advantage in combat',
            'priority': 1,
            'conditions': {
                'combat': True,
                'utility_available': True
            }
        },
        {
            'id': 'save_money',
            'text': 'Consider saving money for next round',
            'priority': 2,
            'conditions': {
                'team_money': 'low',
                'round_time': 'late'
            }
        }
    ],
    'dota2': [
        {
            'id': 'team_fight',
            'text': 'Team fight opportunity! Group up with allies',
            'priority': 1,
            'conditions': {
                'team_alive': 4,
                'combat': True
            }
        },
        {
            'id': 'farm_gold',
            'text': 'Focus on farming to increase gold',
            'priority': 2,
            'conditions': {
                'gold': 'low',
                'combat': False
            }
        }
    ]
}
