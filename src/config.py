"""
Configuration Management
Handles user settings and preferences
"""

import json
import os
from typing import Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class FlickConfig:
    """Configuration settings for Flick"""
    
    # Camera settings
    camera_index: int = 0
    frame_width: int = 640
    frame_height: int = 480
    
    # Hand tracking settings
    max_hands: int = 2
    detection_confidence: float = 0.7
    tracking_confidence: float = 0.7
    
    # Cursor control settings
    cursor_smoothing: float = 1.0  # Cursor movement smoothing (1.0 = instant, lower = smoother)
    gesture_smoothing: int = 3  # Number of frames to smooth hand tracking
    
    # UI settings
    show_hand_landmarks: bool = True
    show_gesture_info: bool = True
    window_width: int = 800
    window_height: int = 600


class ConfigManager:
    """Manages loading and saving configuration"""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize config manager
        
        Args:
            config_path: Path to config file
        """
        self.config_path = config_path
        self.config = FlickConfig()
    
    def load(self) -> FlickConfig:
        """
        Load configuration from file
        
        Returns:
            Loaded configuration
        """
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    
                # Update config with loaded values
                for key, value in data.items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)
                
                print(f"Configuration loaded from {self.config_path}")
                
            except Exception as e:
                print(f"Error loading config: {e}")
                print("Using default configuration")
        else:
            print("No config file found, using defaults")
        
        return self.config
    
    def save(self):
        """Save current configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(asdict(self.config), f, indent=4)
            
            print(f"Configuration saved to {self.config_path}")
            
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self) -> FlickConfig:
        """Get current configuration"""
        return self.config
    
    def update(self, **kwargs):
        """
        Update configuration values
        
        Args:
            **kwargs: Configuration key-value pairs
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                print(f"Updated {key} = {value}")
            else:
                print(f"Warning: Unknown config key '{key}'")
    
    def reset_to_defaults(self):
        """Reset configuration to default values"""
        self.config = FlickConfig()
        print("Configuration reset to defaults")


if __name__ == "__main__":
    # Test config manager
    print("Testing Configuration Manager...")
    
    manager = ConfigManager("test_config.json")
    
    # Load (will use defaults if file doesn't exist)
    config = manager.load()
    print(f"\nCurrent config:")
    print(f"  Camera index: {config.camera_index}")
    print(f"  Volume sensitivity: {config.volume_sensitivity}")
    print(f"  Max hands: {config.max_hands}")
    
    # Update some values
    print("\nUpdating configuration...")
    manager.update(
        volume_sensitivity=1.5,
        crossfader_sensitivity=0.8,
        camera_index=1
    )
    
    # Save
    manager.save()
    
    # Load again to verify
    manager2 = ConfigManager("test_config.json")
    config2 = manager2.load()
    print(f"\nReloaded config:")
    print(f"  Camera index: {config2.camera_index}")
    print(f"  Volume sensitivity: {config2.volume_sensitivity}")
    
    # Clean up test file
    if os.path.exists("test_config.json"):
        os.remove("test_config.json")
    
    print("\nConfig manager test complete!")

