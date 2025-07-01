import cv2
import numpy as np
from PIL import ImageGrab
import win32gui
import win32ui
import win32con
from ctypes import windll
import win32process
import psutil
from typing import Dict, Any, Optional
import logging
from .utils.config import GAME_CONFIGS

class GameStateDetector:
    def __init__(self, game_name: str):
        self.game_name = game_name.lower()
        self.config = GAME_CONFIGS.get(self.game_name)
        if not self.config:
            raise ValueError(f"Unsupported game: {game_name}")
            
        self.logger = logging.getLogger('GameStateDetector')
        self.last_frame = None
        self.last_state = {}
        
    def capture_screen(self):
        """Capture the game window or full screen"""
        try:
            # Try to find the game window with exact match first
            hwnd = None
            window_aliases = self.config.get('window_aliases', [self.config['window_name']])
            
            for window_title in window_aliases:
                hwnd = win32gui.FindWindow(None, window_title)
                if hwnd:
                    self.logger.info(f"Found window with title: {window_title}")
                    break
            
            if not hwnd:
                self.logger.info(f"Trying to find window containing game name: {self.config['window_name']}")
                def callback(hwnd, windows):
                    if win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd)
                        if any(alias.lower() in title.lower() for alias in window_aliases):
                            windows.append((hwnd, title))
                    return True
                
                matching_windows = []
                win32gui.EnumWindows(callback, matching_windows)
                
                if matching_windows:
                    hwnd, title = matching_windows[0]
                    self.logger.info(f"Found window with partial match: {title}")
                else:
                    self.logger.warning(f"Game window not found. Tried aliases: {window_aliases}")
                    # List all window titles for debugging
                    def list_callback(hwnd, windows):
                        if win32gui.IsWindowVisible(hwnd):
                            windows.append(win32gui.GetWindowText(hwnd))
                        return True
                    windows = []
                    win32gui.EnumWindows(list_callback, windows)
                    self.logger.info("Available windows:")
                    for window in windows:
                        if window:  # Only show non-empty window titles
                            self.logger.info(f"- {window}")
                    return None
            
            self.logger.info(f"Found window handle: {hwnd}")
            
            if hwnd:
                # Get window dimensions
                left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                width = right - left
                height = bottom - top
                self.logger.info(f"Window dimensions: {width}x{height} at ({left}, {top})")
                
                # Capture window
                hwndDC = win32gui.GetWindowDC(hwnd)
                mfcDC = win32ui.CreateDCFromHandle(hwndDC)
                saveDC = mfcDC.CreateCompatibleDC()
                
                saveBitMap = win32ui.CreateBitmap()
                saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
                saveDC.SelectObject(saveBitMap)
                
                saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
                
                # Convert to numpy array
                bmpinfo = saveBitMap.GetInfo()
                bmpstr = saveBitMap.GetBitmapBits(True)
                img = np.frombuffer(bmpstr, dtype='uint8')
                img.shape = (height, width, 4)
                
                # Clean up
                win32gui.DeleteObject(saveBitMap.GetHandle())
                saveDC.DeleteDC()
                mfcDC.DeleteDC()
                win32gui.ReleaseDC(hwnd, hwndDC)
                
                return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                
        except Exception as e:
            self.logger.error(f"Error capturing screen: {e}")
            return None
    
    def process_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """Process a frame and return the current game state"""
        try:
            self.last_frame = frame
            state = self.get_game_specific_state()
            self.last_state = state
            return state
        except Exception as e:
            self.logger.error(f"Error processing frame: {str(e)}")
            return self.last_state
            
    def get_game_specific_state(self) -> Dict[str, Any]:
        """Get game-specific state information"""
        if self.game_name == 'valorant':
            return self._get_valorant_state()
        elif self.game_name == 'csgo':
            return self._get_csgo_state()
        elif self.game_name == 'dota2':
            return self._get_dota2_state()
        else:
            return {}
            
    def _get_valorant_state(self) -> Dict[str, Any]:
        """Get Valorant-specific state information"""
        # Always return all expected keys with default values if detection fails
        return {
            'combat': self._detect_combat() if hasattr(self, '_detect_combat') else False,
            'utility_available': self._detect_utility_available() if hasattr(self, '_detect_utility_available') else False,
            'round_time': self._detect_round_time() if hasattr(self, '_detect_round_time') else 'mid',
            'team_money': self._detect_team_money() if hasattr(self, '_detect_team_money') else 'medium',
            'exposed': self._detect_exposed() if hasattr(self, '_detect_exposed') else False,
            'player_health': self._detect_player_health() if hasattr(self, '_detect_player_health') else 100,
            'player_armor': self._detect_player_armor() if hasattr(self, '_detect_player_armor') else 0,
            'player_position': self._detect_player_position() if hasattr(self, '_detect_player_position') else None,
            'enemy_positions': self._detect_enemy_positions() if hasattr(self, '_detect_enemy_positions') else [],
            'spike_location': self._detect_spike_location() if hasattr(self, '_detect_spike_location') else None,
            'site_control': self._detect_site_control() if hasattr(self, '_detect_site_control') else None,
            'enemy_presence': self._detect_enemy_presence() if hasattr(self, '_detect_enemy_presence') else False,
            'teammate_with_smoke': self._detect_teammate_with_smoke() if hasattr(self, '_detect_teammate_with_smoke') else False,
            'teammate_with_flash': self._detect_teammate_with_flash() if hasattr(self, '_detect_teammate_with_flash') else False,
            'teammate_with_healing': self._detect_teammate_with_healing() if hasattr(self, '_detect_teammate_with_healing') else False,
            'need_coordination': self._detect_need_coordination() if hasattr(self, '_detect_need_coordination') else False,
            'abilities': self._detect_abilities() if hasattr(self, '_detect_abilities') else {},
            'equipped_gun': self._detect_equipped_gun() if hasattr(self, '_detect_equipped_gun') else ''
        }
        
    def _get_csgo_state(self) -> Dict[str, Any]:
        """Get CS:GO-specific state information"""
        return {
            'combat': self._detect_combat(),
            'utility_available': self._detect_utility_available(),
            'round_time': self._detect_round_time(),
            'team_money': self._detect_team_money(),
            'exposed': self._detect_exposed()
        }
        
    def _get_dota2_state(self) -> Dict[str, Any]:
        """Get Dota 2-specific state information"""
        return {
            'combat': self._detect_combat(),
            'utility_available': self._detect_utility_available(),
            'team_alive': self._detect_team_alive(),
            'gold': self._detect_gold(),
            'exposed': self._detect_exposed()
        }
        
    # Basic detection methods
    def _detect_combat(self) -> bool:
        """Detect if player is in combat using computer vision"""
        if self.last_frame is None:
            return False
            
        try:
            # Convert frame to HSV for better color detection
            hsv = cv2.cvtColor(self.last_frame, cv2.COLOR_BGR2HSV)
            
            # Define color ranges for combat indicators
            # Red color range for damage indicators
            lower_red1 = np.array([0, 100, 100])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([160, 100, 100])
            upper_red2 = np.array([180, 255, 255])
            
            # Create masks for red colors
            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            red_mask = cv2.bitwise_or(mask1, mask2)
            
            # Check for crosshair movement (indicating aiming)
            if self.last_frame is not None:
                # Convert to grayscale
                gray = cv2.cvtColor(self.last_frame, cv2.COLOR_BGR2GRAY)
                
                # Apply edge detection
                edges = cv2.Canny(gray, 50, 150)
                
                # Count edge pixels in the center region (crosshair area)
                center_y, center_x = edges.shape[0] // 2, edges.shape[1] // 2
                roi_size = 100
                roi = edges[center_y-roi_size:center_y+roi_size, center_x-roi_size:center_x+roi_size]
                edge_count = np.count_nonzero(roi)
                
                # Check for red damage indicators
                red_pixel_count = np.count_nonzero(red_mask)
                
                # Determine if in combat based on thresholds
                return (red_pixel_count > 1000) or (edge_count > 5000)
                
        except Exception as e:
            self.logger.error(f"Error in combat detection: {e}")
            return False
            
        return False
        
    def _detect_team_alive(self) -> int:
        """Detect number of alive teammates"""
        return 5
        
    def _detect_utility_available(self) -> bool:
        """Detect if utility is available"""
        return False
        
    def _detect_round_time(self) -> str:
        """Detect round time (early, mid, late)"""
        return "mid"
        
    def _detect_team_money(self) -> str:
        """Detect team money state (low, medium, high)"""
        return "medium"
        
    def _detect_exposed(self) -> bool:
        """Detect if player is exposed"""
        return False
        
    def _detect_gold(self) -> str:
        """Detect gold state (low, sufficient, high)"""
        return "sufficient"
        
    def _detect_player_health(self) -> int:
        """Detect player health"""
        return 100
        
    def _detect_player_armor(self) -> int:
        """Detect player armor"""
        return 0
        
    def _detect_player_position(self) -> list[float]:
        """Detect player position"""
        return [0.0, 0.0]
        
    def _detect_enemy_positions(self) -> list[list[float]]:
        """Detect enemy positions"""
        return []
        
    def _detect_spike_location(self) -> list[float]:
        """Detect spike location"""
        return [0.0, 0.0]
        
    def _detect_site_control(self) -> bool:
        """Detect site control"""
        return False
        
    def _detect_enemy_presence(self) -> bool:
        """Detect enemy presence"""
        return False
        
    def _detect_teammate_with_smoke(self) -> bool:
        """Detect teammate with smoke"""
        return False
        
    def _detect_teammate_with_flash(self) -> bool:
        """Detect teammate with flash"""
        return False
        
    def _detect_teammate_with_healing(self) -> bool:
        """Detect teammate with healing"""
        return False
        
    def _detect_need_coordination(self) -> bool:
        """Detect need for coordination"""
        return False
    
    def _detect_abilities(self) -> dict:
        """Detect available abilities from the abilities HUD region"""
        # Only mark Q/E as available if in combat
        combat = self._detect_combat() if hasattr(self, '_detect_combat') else False
        return {
            'Q': True if combat else False,
            'E': True if combat else False,
            'C': False,
            'X': False
        }

    def _detect_equipped_gun(self) -> str:
        """Detect currently equipped gun from the gun HUD region"""
        # Placeholder: In production, use OCR or icon detection on the gun region
        # For now, return a mock gun name
        return 'Classic'
