from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QCheckBox, QSlider, QComboBox,
                            QGroupBox, QSpinBox, QColorDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
import json
import os

class SettingsDialog(QDialog):
    # Signal to notify overlay of settings changes
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI Game Assistant Settings")
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """Setup the settings dialog UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Appearance Group
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QVBoxLayout()
        
        # Transparency
        transparency_layout = QHBoxLayout()
        transparency_label = QLabel("Overlay Transparency:")
        self.transparency_slider = QSlider(Qt.Orientation.Horizontal)
        self.transparency_slider.setRange(50, 100)
        self.transparency_slider.setValue(80)
        self.transparency_slider.valueChanged.connect(self.on_transparency_changed)
        transparency_layout.addWidget(transparency_label)
        transparency_layout.addWidget(self.transparency_slider)
        appearance_layout.addLayout(transparency_layout)
        
        # Theme Selection
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "Custom"])
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        appearance_layout.addLayout(theme_layout)
        
        # Custom Colors
        colors_layout = QHBoxLayout()
        self.custom_colors_btn = QPushButton("Custom Colors")
        self.custom_colors_btn.clicked.connect(self.show_color_dialog)
        colors_layout.addWidget(self.custom_colors_btn)
        appearance_layout.addLayout(colors_layout)
        
        appearance_group.setLayout(appearance_layout)
        layout.addWidget(appearance_group)
        
        # Notifications Group
        notifications_group = QGroupBox("Notifications")
        notifications_layout = QVBoxLayout()
        
        # Sound Notifications
        self.sound_checkbox = QCheckBox("Enable Sound Notifications")
        self.sound_checkbox.setChecked(True)
        notifications_layout.addWidget(self.sound_checkbox)
        
        # Sound Volume
        volume_layout = QHBoxLayout()
        volume_label = QLabel("Notification Volume:")
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)
        notifications_layout.addLayout(volume_layout)
        
        notifications_group.setLayout(notifications_layout)
        layout.addWidget(notifications_group)
        
        # Game Settings Group
        game_group = QGroupBox("Game Settings")
        game_layout = QVBoxLayout()
        
        # Game Selection
        game_select_layout = QHBoxLayout()
        game_label = QLabel("Game:")
        self.game_combo = QComboBox()
        self.game_combo.addItems(["Valorant", "CS:GO", "Dota 2"])
        game_select_layout.addWidget(game_label)
        game_select_layout.addWidget(self.game_combo)
        game_layout.addLayout(game_select_layout)
        
        # Update Interval
        interval_layout = QHBoxLayout()
        interval_label = QLabel("Update Interval (ms):")
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(100, 5000)
        self.interval_spin.setValue(1000)
        self.interval_spin.setSingleStep(100)
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_spin)
        game_layout.addLayout(interval_layout)
        
        game_group.setLayout(game_layout)
        layout.addWidget(game_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        # Set dialog size
        self.setMinimumWidth(400)
        
    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as f:
                    settings = json.load(f)
                    
                # Apply loaded settings
                self.transparency_slider.setValue(settings.get('transparency', 80))
                self.theme_combo.setCurrentText(settings.get('theme', 'Dark'))
                self.sound_checkbox.setChecked(settings.get('sound_enabled', True))
                self.volume_slider.setValue(settings.get('volume', 50))
                self.game_combo.setCurrentText(settings.get('game', 'Valorant'))
                self.interval_spin.setValue(settings.get('update_interval', 1000))
        except Exception as e:
            print(f"Error loading settings: {e}")
            
    def save_settings(self):
        """Save settings to file"""
        settings = {
            'transparency': self.transparency_slider.value(),
            'theme': self.theme_combo.currentText(),
            'sound_enabled': self.sound_checkbox.isChecked(),
            'volume': self.volume_slider.value(),
            'game': self.game_combo.currentText(),
            'update_interval': self.interval_spin.value()
        }
        
        try:
            with open('settings.json', 'w') as f:
                json.dump(settings, f)
            self.settings_changed.emit(settings)
            self.accept()
        except Exception as e:
            print(f"Error saving settings: {e}")
            
    def on_transparency_changed(self, value):
        """Handle transparency slider change"""
        self.settings_changed.emit({'transparency': value})
        
    def on_theme_changed(self, theme):
        """Handle theme selection change"""
        self.settings_changed.emit({'theme': theme})
        
    def show_color_dialog(self):
        """Show color picker dialog"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.settings_changed.emit({'custom_color': color.name()}) 