"""
Flick - Hand Gesture DJ Controller
Main application entry point
"""

import sys
import time
import threading
from typing import Optional

from hand_tracker import HandTracker
from gesture_engine import GestureEngine, DJControl
from browser_controller import YouDJController
from config import ConfigManager
from ui.main_window import FlickUI


class FlickApp:
    """Main application controller"""
    
    def __init__(self):
        """Initialize the Flick application"""
        # Load configuration
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load()
        
        # Initialize components
        self.hand_tracker = HandTracker(
            max_hands=self.config.max_hands,
            detection_confidence=self.config.detection_confidence,
            tracking_confidence=self.config.tracking_confidence
        )
        
        self.gesture_engine = GestureEngine()
        self.gesture_engine.set_sensitivity('volume', self.config.volume_sensitivity)
        self.gesture_engine.set_sensitivity('crossfader', self.config.crossfader_sensitivity)
        self.gesture_engine.set_sensitivity('filter', self.config.filter_sensitivity)
        
        self.browser_controller = YouDJController()
        
        # Initialize UI
        self.ui = FlickUI(
            on_start=self.start_tracking,
            on_stop=self.stop_tracking,
            on_sensitivity_change=self.on_sensitivity_change
        )
        
        # Runtime state
        self.is_running = False
        self.tracking_thread: Optional[threading.Thread] = None
        
        print("Flick initialized successfully!")
    
    def start_tracking(self):
        """Start the hand tracking and gesture control"""
        if self.is_running:
            return
        
        print("Starting Flick...")
        
        # Start camera
        if not self.hand_tracker.start_camera(self.config.camera_index):
            self.ui.show_error("Failed to start camera. Please check your webcam connection.")
            return
        
        # Start browser
        if not self.browser_controller.start(headless=self.config.browser_headless):
            self.ui.show_error("Failed to start browser controller.")
            self.hand_tracker.stop_camera()
            return
        
        # Start tracking thread
        self.is_running = True
        self.tracking_thread = threading.Thread(target=self._tracking_loop, daemon=True)
        self.tracking_thread.start()
        
        print("Flick is running! Control YouDJ with your hands.")
        self.ui.show_info("Flick is now active! Position your hands in front of the camera.")
    
    def stop_tracking(self):
        """Stop the hand tracking and gesture control"""
        if not self.is_running:
            return
        
        print("Stopping Flick...")
        
        self.is_running = False
        
        # Wait for tracking thread to finish
        if self.tracking_thread and self.tracking_thread.is_alive():
            self.tracking_thread.join(timeout=2.0)
        
        # Stop components
        self.hand_tracker.stop_camera()
        self.browser_controller.stop()
        self.gesture_engine.reset()
        
        print("Flick stopped.")
    
    def _tracking_loop(self):
        """Main tracking loop (runs in separate thread)"""
        try:
            while self.is_running:
                # Process frame from camera
                frame, hands_data = self.hand_tracker.process_frame()
                
                if frame is not None:
                    # Update UI with video feed
                    self.ui.update_video_frame(frame)
                
                if hands_data:
                    # Process gestures
                    controls = self.gesture_engine.process_hands(hands_data)
                    
                    # Execute controls on YouDJ
                    self._execute_controls(controls)
                    
                    # Update UI status
                    self._update_ui_status(hands_data, controls)
                else:
                    # No hands detected
                    self._update_ui_status_no_hands()
                
                # Small delay to control frame rate
                time.sleep(0.033)  # ~30 FPS
                
        except Exception as e:
            print(f"Error in tracking loop: {e}")
            import traceback
            traceback.print_exc()
    
    def _execute_controls(self, controls: list):
        """
        Execute DJ controls on the browser
        
        Args:
            controls: List of DJControl objects
        """
        for control in controls:
            try:
                if control.control_type == 'crossfader':
                    self.browser_controller.set_crossfader(control.value)
                    
                elif control.control_type == 'volume_left':
                    self.browser_controller.set_volume('left', control.value)
                    
                elif control.control_type == 'volume_right':
                    self.browser_controller.set_volume('right', control.value)
                    
                elif control.control_type == 'play_left':
                    self.browser_controller.play_deck('left')
                    
                elif control.control_type == 'play_right':
                    self.browser_controller.play_deck('right')
                    
                elif control.control_type == 'pause_left':
                    self.browser_controller.pause_deck('left')
                    
                elif control.control_type == 'pause_right':
                    self.browser_controller.pause_deck('right')
                    
                elif control.control_type == 'filter':
                    self.browser_controller.set_filter(control.value)
                    
                elif control.control_type == 'toggle_effect':
                    self.browser_controller.toggle_effect()
                    
            except Exception as e:
                print(f"Error executing control {control.control_type}: {e}")
    
    def _update_ui_status(self, hands_data: list, controls: list):
        """
        Update UI with current gesture status
        
        Args:
            hands_data: Hand tracking data
            controls: List of DJ controls
        """
        status = {}
        
        # Hand detection status
        left_detected = any(h['label'] == 'Left' for h in hands_data)
        right_detected = any(h['label'] == 'Right' for h in hands_data)
        
        status['left_hand'] = "✅ Detected" if left_detected else "❌ Not detected"
        status['right_hand'] = "✅ Detected" if right_detected else "❌ Not detected"
        
        # Control values
        for control in controls:
            if control.control_type in ['crossfader', 'volume_left', 'volume_right', 'filter']:
                display_value = f"{control.value:.2f}"
                
                if control.control_type == 'crossfader':
                    status['crossfader'] = display_value
                elif control.control_type == 'volume_left':
                    status['volume_left'] = display_value
                elif control.control_type == 'volume_right':
                    status['volume_right'] = display_value
                elif control.control_type == 'filter':
                    status['filter'] = display_value
        
        self.ui.update_gesture_status(status)
    
    def _update_ui_status_no_hands(self):
        """Update UI when no hands are detected"""
        status = {
            'left_hand': "❌ Not detected",
            'right_hand': "❌ Not detected",
            'crossfader': "--",
            'volume_left': "--",
            'volume_right': "--",
            'filter': "--"
        }
        self.ui.update_gesture_status(status)
    
    def on_sensitivity_change(self, control: str, value: float):
        """
        Handle sensitivity slider changes
        
        Args:
            control: Control name ('volume', 'crossfader', 'filter')
            value: New sensitivity value
        """
        self.gesture_engine.set_sensitivity(control, value)
        
        # Update config
        if control == 'volume':
            self.config_manager.update(volume_sensitivity=value)
        elif control == 'crossfader':
            self.config_manager.update(crossfader_sensitivity=value)
        elif control == 'filter':
            self.config_manager.update(filter_sensitivity=value)
        
        # Save config
        self.config_manager.save()
    
    def run(self):
        """Run the application"""
        try:
            print("=" * 50)
            print("✋ FLICK - Hand Gesture DJ Controller")
            print("=" * 50)
            print("\nStarting application...")
            
            # Run UI (blocking call)
            self.ui.run()
            
        except KeyboardInterrupt:
            print("\nShutting down...")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("Cleaning up...")
        
        self.stop_tracking()
        self.hand_tracker.cleanup()
        
        print("Goodbye! 🎵")


def main():
    """Main entry point"""
    app = FlickApp()
    app.run()


if __name__ == "__main__":
    main()

