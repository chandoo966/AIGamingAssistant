from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QRectF
from PyQt6.QtGui import QFont, QIcon, QColor, QPainter, QPainterPath, QPalette
import logging
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtCore import QUrl
import os
import json
from .settings_dialog import SettingsDialog

class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('OverlayWindow')
        self.settings = self.load_settings()
        self.is_minimized = False
        self.oldPos = None  # Initialize oldPos
        self.setup_ui()
        self.setup_sounds()
        self.apply_settings()
        
    def load_settings(self):
        """Load settings from file"""
        default_settings = {
            'transparency': 80,
            'theme': 'Dark',
            'sound_enabled': True,
            'volume': 50,
            'game': 'Valorant',
            'update_interval': 1000
        }
        
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
            
        return default_settings
        
    def apply_settings(self):
        """Apply current settings to the overlay"""
        try:
            # Apply transparency
            opacity = self.settings.get('transparency', 80) / 100.0
            self.setWindowOpacity(opacity)
            
            # Apply theme
            theme = self.settings.get('theme', 'Dark')
            if theme == 'Light':
                self.apply_light_theme()
            elif theme == 'Dark':
                self.apply_dark_theme()
            
            # Apply sound settings
            if self.critical_sound:
                self.critical_sound.setVolume(self.settings.get('volume', 50) / 100.0)
                
        except Exception as e:
            self.logger.error(f"Error applying settings: {e}")
            
    def apply_dark_theme(self):
        """Apply dark theme colors"""
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 30, 0.6);
                color: white;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                color: white;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        
    def apply_light_theme(self):
        """Apply light theme colors"""
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(240, 240, 240, 0.6);
                color: black;
            }
            QLabel {
                color: black;
            }
            QPushButton {
                color: black;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
            }
        """)
        
    def setup_sounds(self):
        """Setup sound effects for notifications"""
        try:
            # Use system beep instead of WAV file
            self.critical_sound = QSoundEffect()
            self.critical_sound.setSource(QUrl.fromLocalFile(":/sounds/beep.wav"))
            self.critical_sound.setVolume(0.5)
        except Exception as e:
            self.logger.error(f"Error setting up sounds: {e}")
            self.critical_sound = None
        
    def setup_ui(self):
        """Setup the overlay UI"""
        try:
            # Set window properties
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            
            # Create main layout
            main_layout = QVBoxLayout()
            main_layout.setContentsMargins(10, 10, 10, 10)
            self.setLayout(main_layout)
            
            # Create header with controls
            header = QHBoxLayout()
            
            # Title label
            title = QLabel("AI Game Assistant")
            title.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                }
            """)
            header.addWidget(title)
            
            # Control buttons
            controls = QHBoxLayout()
            controls.setSpacing(5)
            
            # Settings button
            self.settings_btn = QPushButton("⚙")
            self.settings_btn.setFixedSize(24, 24)
            self.settings_btn.clicked.connect(self.show_settings)
            controls.addWidget(self.settings_btn)
            
            # Minimize button
            self.minimize_btn = QPushButton("−")
            self.minimize_btn.setFixedSize(24, 24)
            self.minimize_btn.clicked.connect(self.toggle_minimize)
            controls.addWidget(self.minimize_btn)
            
            # Close button
            self.close_btn = QPushButton("×")
            self.close_btn.setFixedSize(24, 24)
            self.close_btn.clicked.connect(self.close)
            controls.addWidget(self.close_btn)
            
            header.addLayout(controls)
            main_layout.addLayout(header)
            
            # Create content frame
            self.content_frame = QFrame()
            self.content_frame.setStyleSheet("""
                QFrame {
                    background-color: rgba(30, 30, 30, 0.6);
                    border-radius: 10px;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }
            """)
            content_layout = QVBoxLayout()
            content_layout.setContentsMargins(10, 10, 10, 10)
            content_layout.setSpacing(8)
            self.content_frame.setLayout(content_layout)
            
            # Create suggestion labels
            self.suggestion_labels = []
            for _ in range(3):  # Create 3 labels for top 3 suggestions
                label = QLabel()
                label.setStyleSheet("""
                    QLabel {
                        color: white;
                        background-color: rgba(40, 40, 40, 0.9);
                        padding: 12px;
                        border-radius: 8px;
                        margin-bottom: 8px;
                        font-size: 12px;
                    }
                """)
                label.setFont(QFont('Segoe UI', 12))
                label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
                label.setWordWrap(True)
                content_layout.addWidget(label)
                self.suggestion_labels.append(label)
            
            main_layout.addWidget(self.content_frame)
            
            # Set initial position and size
            self.setGeometry(100, 100, 350, 250)
            
            # Apply styles to control buttons
            for btn in [self.settings_btn, self.minimize_btn, self.close_btn]:
                btn.setStyleSheet("""
                    QPushButton {
                        color: white;
                        background-color: transparent;
                        border: none;
                        font-size: 16px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: rgba(255, 255, 255, 0.1);
                        border-radius: 12px;
                    }
                """)
            
        except Exception as e:
            self.logger.error(f"Error setting up UI: {e}")
            
    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self)
        dialog.settings_changed.connect(self.on_settings_changed)
        dialog.exec()
        
    def on_settings_changed(self, new_settings):
        """Handle settings changes"""
        self.settings.update(new_settings)
        self.apply_settings()
        
    def toggle_minimize(self):
        """Toggle minimize state"""
        if self.is_minimized:
            self.content_frame.show()
            self.minimize_btn.setText("−")
            self.setFixedHeight(250)
        else:
            self.content_frame.hide()
            self.minimize_btn.setText("+")
            self.setFixedHeight(50)
        self.is_minimized = not self.is_minimized
            
    def update_suggestions(self, suggestions: list):
        """Update the suggestion display"""
        try:
            self.logger.info(f"Overlay displaying {len(suggestions)} suggestions: {[{'text': s.get('text'), 'priority': s.get('priority')} for s in suggestions]}")
            if not self.suggestion_labels:
                return
                
            # Clear all labels first
            for label in self.suggestion_labels:
                label.setText("")
                label.setStyleSheet("""
                    QLabel {
                        color: white;
                        background-color: rgba(40, 40, 40, 0.9);
                        padding: 12px;
                        border-radius: 8px;
                        margin-bottom: 8px;
                        font-size: 12px;
                    }
                """)
            
            # Update labels with new suggestions
            for i, suggestion in enumerate(suggestions):
                if i < len(self.suggestion_labels):
                    label = self.suggestion_labels[i]
                    label.setText(suggestion.get('text', ''))
                    
                    # Apply different styles based on priority
                    priority = suggestion.get('priority', 3)
                    if priority == 1:
                        label.setStyleSheet("""
                            QLabel {
                                color: white;
                                background-color: rgba(220, 53, 69, 0.9);
                                padding: 12px;
                                border-radius: 8px;
                                margin-bottom: 8px;
                                font-size: 12px;
                                font-weight: bold;
                            }
                        """)
                    elif priority == 2:
                        label.setStyleSheet("""
                            QLabel {
                                color: white;
                                background-color: rgba(255, 193, 7, 0.9);
                                padding: 12px;
                                border-radius: 8px;
                                margin-bottom: 8px;
                                font-size: 12px;
                            }
                        """)
                    
                    # Play sound for high priority suggestions
                    if priority == 1 and self.critical_sound and self.settings.get('sound_enabled', True):
                        self.critical_sound.play()
            
            # Show the window if it was hidden
            if not self.isVisible():
                self.show()
                
        except Exception as e:
            self.logger.error(f"Error updating suggestions: {e}")
            
    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        self.oldPos = event.globalPosition().toPoint()
        
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        delta = event.globalPosition().toPoint() - self.oldPos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPosition().toPoint()
        
    def paintEvent(self, event):
        """Custom paint event for rounded corners and transparency"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Create path for rounded rectangle
        path = QPainterPath()
        rect = QRectF(self.rect())  # Convert QRect to QRectF
        path.addRoundedRect(rect, 10, 10)
        
        # Set up painter for transparency
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.palette().color(QPalette.ColorRole.Window))
        
        # Draw the rounded rectangle
        painter.drawPath(path)
        
        # Draw the content
        super().paintEvent(event)

def create_overlay() -> OverlayWindow:
    """Create and return an overlay window instance"""
    return OverlayWindow()