"""
Flick - Hand Gesture Mouse Controller
Main application entry point
"""

import time
import threading
from typing import Optional

from hand_tracker import HandTracker
from mouse_controller import MouseController
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
        
        self.mouse_controller = MouseController()
        
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
        
        # Start tracking thread
        self.is_running = True
        self.tracking_thread = threading.Thread(target=self._tracking_loop, daemon=True)
        self.tracking_thread.start()
        
        print("Flick is running! Control your mouse with hand gestures.")
        self.ui.show_info("Flick is now active! Move your hand to control the cursor.")
    
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
        self.mouse_controller.cleanup()
        
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
                    # Use primary hand (right hand if available, else left)
                    primary_hand = None
                    for hand in hands_data:
                        if hand['label'] == 'Right':
                            primary_hand = hand
                            break
                    if not primary_hand and hands_data:
                        primary_hand = hands_data[0]
                    
                    # Update mouse controller with primary hand
                    if primary_hand:
                        self.mouse_controller.update_from_hand(primary_hand)
                    
                    # Update UI status
                    self._update_ui_status_mouse(hands_data)
                else:
                    # No hands detected
                    self._update_ui_status_no_hands()
                
                # Small delay to control frame rate
                time.sleep(0.033)  # ~30 FPS
                
        except Exception as e:
            print(f"Error in tracking loop: {e}")
            import traceback
            traceback.print_exc()
    
    def _update_ui_status_mouse(self, hands_data: list):
        """
        Update UI with current mouse control status
        
        Args:
            hands_data: Hand tracking data
        """
        status = {}
        
        # Hand detection status
        left_detected = any(h['label'] == 'Left' for h in hands_data)
        right_detected = any(h['label'] == 'Right' for h in hands_data)
        
        status['left_hand'] = "✅ Detected" if left_detected else "❌ Not detected"
        status['right_hand'] = "✅ Detected" if right_detected else "❌ Not detected"
        
        # Get primary hand gestures
        primary_hand = None
        for hand in hands_data:
            if hand['label'] == 'Right':
                primary_hand = hand
                break
        if not primary_hand and hands_data:
            primary_hand = hands_data[0]
        
        if primary_hand:
            # Show active gestures
            gestures = []
            if primary_hand.get('is_pointing'):
                gestures.append('👆 CLICK')
            if primary_hand.get('is_pinching'):
                gestures.append('🤏 DRAG')
            if primary_hand.get('is_peace'):
                gestures.append('✌️ RIGHT-CLICK')
            if primary_hand.get('is_open'):
                gestures.append('🫳 OPEN')
            if not primary_hand.get('is_open') and not any([primary_hand.get('is_pointing'), primary_hand.get('is_pinching'), primary_hand.get('is_peace')]):
                gestures.append('✊ CLOSED')
            
            status['crossfader'] = " | ".join(gestures) if gestures else "Move cursor"
            status['volume_left'] = f"X: {primary_hand['palm_position']['x']:.2f}"
            status['volume_right'] = f"Y: {primary_hand['palm_position']['y']:.2f}"
            status['filter'] = "Mouse mode"
        else:
            status['crossfader'] = "--"
            status['volume_left'] = "--"
            status['volume_right'] = "--"
            status['filter'] = "--"
        
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
        Handle sensitivity slider changes (for cursor smoothing)
        
        Args:
            control: Control name (currently unused, kept for UI compatibility)
            value: New sensitivity value
        """
        # Map sensitivity to cursor smoothing (inverse: higher sensitivity = less smoothing)
        smoothing = 1.0 / max(value, 0.1)  # Prevent division by zero
        smoothing = min(smoothing, 1.0)  # Cap at 1.0 (instant response)
        self.mouse_controller.set_smooth_factor(smoothing)
        
        # Update config
        self.config_manager.update(cursor_smoothing=value)
        self.config_manager.save()
    
    def run(self):
        """Run the application"""
        try:
            print("=" * 50)
            print("✋ FLICK - Hand Gesture Mouse Controller")
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
        self.mouse_controller.cleanup()
        
        print("Goodbye! 🎵")


def main():
    """Main entry point"""
    app = FlickApp()
    app.run()


if __name__ == "__main__":
    main()

