"""
Gesture Recognition Engine
Interprets hand tracking data and maps it to DJ control commands
"""

import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class GestureType(Enum):
    """Types of gestures recognized"""
    NONE = "none"
    PLAY = "play"
    PAUSE = "pause"
    VOLUME_ADJUST = "volume_adjust"
    CROSSFADE_ADJUST = "crossfade_adjust"
    FILTER_ADJUST = "filter_adjust"
    PINCH_EFFECT = "pinch_effect"
    SWIPE_LEFT = "swipe_left"
    SWIPE_RIGHT = "swipe_right"
    CLICK = "click"
    PEACE_SIGN = "peace_sign"
    THUMBS_UP = "thumbs_up"


@dataclass
class DJControl:
    """Represents a DJ control command"""
    control_type: str  # 'crossfader', 'volume_left', 'volume_right', 'play_left', 'play_right', 'filter'
    value: float  # Normalized value 0-1 for sliders, or binary for buttons
    hand: str  # 'Left' or 'Right'


class GestureEngine:
    """Converts hand tracking data into DJ control commands"""
    
    def __init__(self):
        """Initialize the gesture engine"""
        # Sensitivity settings (can be adjusted)
        self.volume_sensitivity = 1.0
        self.crossfader_sensitivity = 1.0
        self.filter_sensitivity = 1.0
        
        # Dead zones to prevent jitter
        self.dead_zone = 0.02
        
        # Previous hand positions for tracking movement
        self.prev_positions = {}
        
        # Gesture state tracking
        self.left_hand_playing = False
        self.right_hand_playing = False
        self.pinch_effect_active = False
        self.left_hand_pointing = False
        self.right_hand_pointing = False
        
        # Smoothing buffer for stability
        self.position_buffer = {
            'left': [],
            'right': []
        }
        self.buffer_size = 3
    
    def process_hands(self, hands_data: Optional[List[Dict]]) -> List[DJControl]:
        """
        Process hand tracking data and generate DJ control commands
        
        Args:
            hands_data: List of hand info dictionaries from HandTracker
            
        Returns:
            List of DJControl commands to execute
        """
        if not hands_data:
            return []
        
        controls = []
        
        # Organize hands by left/right
        left_hand = None
        right_hand = None
        
        for hand in hands_data:
            if hand['label'] == 'Left':
                left_hand = hand
            elif hand['label'] == 'Right':
                right_hand = hand
        
        # Process left hand (controls crossfader and left deck)
        if left_hand:
            controls.extend(self._process_left_hand(left_hand))
        
        # Process right hand (controls right deck and filters)
        if right_hand:
            controls.extend(self._process_right_hand(right_hand))
        
        # Process two-hand gestures
        if left_hand and right_hand:
            controls.extend(self._process_two_hand_gestures(left_hand, right_hand))
        
        return controls
    
    def _smooth_position(self, position: Dict, hand_label: str) -> Dict:
        """
        Smooth hand position using moving average
        
        Args:
            position: Position dictionary with x, y, z
            hand_label: 'Left' or 'Right'
            
        Returns:
            Smoothed position
        """
        hand_key = hand_label.lower()
        
        # Add to buffer
        self.position_buffer[hand_key].append(position)
        
        # Keep buffer size limited
        if len(self.position_buffer[hand_key]) > self.buffer_size:
            self.position_buffer[hand_key].pop(0)
        
        # Calculate average
        avg_x = np.mean([p['x'] for p in self.position_buffer[hand_key]])
        avg_y = np.mean([p['y'] for p in self.position_buffer[hand_key]])
        avg_z = np.mean([p['z'] for p in self.position_buffer[hand_key]])
        
        return {'x': avg_x, 'y': avg_y, 'z': avg_z}
    
    def _process_left_hand(self, hand: Dict) -> List[DJControl]:
        """
        Process left hand gestures
        - X position: Crossfader
        - Y position: Left deck volume
        - Open/Closed: Play/Pause left deck
        
        Args:
            hand: Hand info dictionary
            
        Returns:
            List of control commands
        """
        controls = []
        palm = self._smooth_position(hand['palm_position'], 'Left')
        
        # Crossfader control (X position: 0=left, 1=right)
        # Map to YouDJ crossfader (we want 0=full left, 0.5=center, 1=full right)
        crossfader_value = palm['x']
        controls.append(DJControl(
            control_type='crossfader',
            value=crossfader_value,
            hand='Left'
        ))
        
        # Left deck volume (Y position: higher hand = louder)
        # Invert Y (0 at top, 1 at bottom in screen coords)
        volume_value = 1.0 - palm['y']
        # Apply sensitivity
        volume_value = np.clip(volume_value * self.volume_sensitivity, 0.0, 1.0)
        
        controls.append(DJControl(
            control_type='volume_left',
            value=volume_value,
            hand='Left'
        ))
        
        # Play/Pause based on hand open/closed (only if not pointing)
        if not hand.get('is_pointing', False):
            if hand['is_open'] and not self.left_hand_playing:
                controls.append(DJControl(
                    control_type='play_left',
                    value=1.0,
                    hand='Left'
                ))
                self.left_hand_playing = True
            elif not hand['is_open'] and self.left_hand_playing:
                controls.append(DJControl(
                    control_type='pause_left',
                    value=0.0,
                    hand='Left'
                ))
                self.left_hand_playing = False
        
        # Click gesture (pointing)
        if hand.get('is_pointing', False) and not self.left_hand_pointing:
            controls.append(DJControl(
                control_type='click',
                value=palm['x'],  # X position of click
                hand='Left'
            ))
            controls.append(DJControl(
                control_type='click_y',
                value=palm['y'],  # Y position of click
                hand='Left'
            ))
            self.left_hand_pointing = True
        elif not hand.get('is_pointing', False):
            self.left_hand_pointing = False
        
        return controls
    
    def _process_right_hand(self, hand: Dict) -> List[DJControl]:
        """
        Process right hand gestures
        - X position: Filter amount
        - Y position: Right deck volume
        - Open/Closed: Play/Pause right deck
        
        Args:
            hand: Hand info dictionary
            
        Returns:
            List of control commands
        """
        controls = []
        palm = self._smooth_position(hand['palm_position'], 'Right')
        
        # Filter control (X position)
        filter_value = palm['x']
        controls.append(DJControl(
            control_type='filter',
            value=filter_value,
            hand='Right'
        ))
        
        # Right deck volume (Y position: higher hand = louder)
        volume_value = 1.0 - palm['y']
        volume_value = np.clip(volume_value * self.volume_sensitivity, 0.0, 1.0)
        
        controls.append(DJControl(
            control_type='volume_right',
            value=volume_value,
            hand='Right'
        ))
        
        # Play/Pause based on hand open/closed (only if not pointing)
        if not hand.get('is_pointing', False):
            if hand['is_open'] and not self.right_hand_playing:
                controls.append(DJControl(
                    control_type='play_right',
                    value=1.0,
                    hand='Right'
                ))
                self.right_hand_playing = True
            elif not hand['is_open'] and self.right_hand_playing:
                controls.append(DJControl(
                    control_type='pause_right',
                    value=0.0,
                    hand='Right'
                ))
                self.right_hand_playing = False
        
        # Click gesture (pointing)
        if hand.get('is_pointing', False) and not self.right_hand_pointing:
            controls.append(DJControl(
                control_type='click',
                value=palm['x'],  # X position of click
                hand='Right'
            ))
            controls.append(DJControl(
                control_type='click_y',
                value=palm['y'],  # Y position of click
                hand='Right'
            ))
            self.right_hand_pointing = True
        elif not hand.get('is_pointing', False):
            self.right_hand_pointing = False
        
        return controls
    
    def _process_two_hand_gestures(self, left_hand: Dict, right_hand: Dict) -> List[DJControl]:
        """
        Process gestures that require both hands
        - Both hands pinching: Toggle effects
        
        Args:
            left_hand: Left hand info
            right_hand: Right hand info
            
        Returns:
            List of control commands
        """
        controls = []
        
        # Check if both hands are pinching (trigger effect)
        if left_hand['is_pinching'] and right_hand['is_pinching']:
            if not self.pinch_effect_active:
                controls.append(DJControl(
                    control_type='toggle_effect',
                    value=1.0,
                    hand='Both'
                ))
                self.pinch_effect_active = True
        else:
            if self.pinch_effect_active:
                self.pinch_effect_active = False
        
        return controls
    
    def reset(self):
        """Reset gesture engine state"""
        self.left_hand_playing = False
        self.right_hand_playing = False
        self.pinch_effect_active = False
        self.prev_positions = {}
        self.position_buffer = {'left': [], 'right': []}
    
    def set_sensitivity(self, control: str, value: float):
        """
        Adjust sensitivity for a control
        
        Args:
            control: 'volume', 'crossfader', or 'filter'
            value: Sensitivity multiplier (0.5 to 2.0 recommended)
        """
        if control == 'volume':
            self.volume_sensitivity = np.clip(value, 0.1, 3.0)
        elif control == 'crossfader':
            self.crossfader_sensitivity = np.clip(value, 0.1, 3.0)
        elif control == 'filter':
            self.filter_sensitivity = np.clip(value, 0.1, 3.0)


if __name__ == "__main__":
    # Test the gesture engine
    print("Testing Gesture Engine...")
    
    engine = GestureEngine()
    
    # Simulate hand data
    test_hand_data = [
        {
            'label': 'Left',
            'palm_position': {'x': 0.3, 'y': 0.5, 'z': 0.0},
            'is_open': True,
            'is_pinching': False
        },
        {
            'label': 'Right',
            'palm_position': {'x': 0.7, 'y': 0.4, 'z': 0.0},
            'is_open': True,
            'is_pinching': False
        }
    ]
    
    controls = engine.process_hands(test_hand_data)
    
    print("\nGenerated controls:")
    for control in controls:
        print(f"  {control.control_type}: {control.value:.2f} ({control.hand} hand)")
    
    print("\nGesture engine test complete!")

