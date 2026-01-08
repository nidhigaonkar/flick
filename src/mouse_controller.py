"""
Mouse Controller
Controls the system mouse cursor directly using hand gestures
"""

import pyautogui
import time
from typing import Dict, Optional
import numpy as np


class MouseController:
    """Controls system mouse based on hand gestures"""
    
    def __init__(self):
        """Initialize the mouse controller"""
        # Get screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()
        
        # Safety settings
        pyautogui.FAILSAFE = True  # Move mouse to corner to abort
        pyautogui.PAUSE = 0.01  # Small pause between actions
        
        # Smoothing for cursor movement
        self.smooth_factor = 0.3  # Lower = smoother but slower response
        self.last_cursor_x = self.screen_width / 2
        self.last_cursor_y = self.screen_height / 2
        
        # Gesture state tracking
        self.is_dragging = False
        self.last_click_time = 0
        self.click_cooldown = 0.3  # Seconds between clicks
        
        # Scroll state tracking
        self.is_scrolling = False
        self.last_scroll_y = None
        self.scroll_threshold = 0.02  # Minimum Y movement to trigger scroll
        self.scroll_cooldown = 0.1  # Seconds between scroll events
        
        # Dead zone (small movements ignored)
        self.dead_zone = 5  # pixels
        
        print(f"Mouse controller initialized. Screen: {self.screen_width}x{self.screen_height}")
    
    def update_from_hand(self, hand_data: Dict):
        """
        Update mouse position and state based on hand data
        
        Args:
            hand_data: Hand information from hand tracker
        """
        if not hand_data:
            return
        
        palm_pos = hand_data['palm_position']
        
        # Convert normalized hand position (0-1) to screen coordinates
        # Direct mapping: hand left = cursor left, hand right = cursor right
        target_x = int(palm_pos['x'] * self.screen_width)
        target_y = int(palm_pos['y'] * self.screen_height)
        
        # Apply smoothing to cursor movement
        cursor_x = self.last_cursor_x + (target_x - self.last_cursor_x) * self.smooth_factor
        cursor_y = self.last_cursor_y + (target_y - self.last_cursor_y) * self.smooth_factor
        
        # Check dead zone
        dx = abs(cursor_x - self.last_cursor_x)
        dy = abs(cursor_y - self.last_cursor_y)
        
        if dx > self.dead_zone or dy > self.dead_zone:
            # Move mouse cursor
            try:
                pyautogui.moveTo(cursor_x, cursor_y, duration=0)
                self.last_cursor_x = cursor_x
                self.last_cursor_y = cursor_y
            except Exception as e:
                pass  # Ignore failsafe exceptions
        
        # Handle gestures
        self._handle_gestures(hand_data)
    
    def _handle_gestures(self, hand_data: Dict):
        """
        Handle click and drag gestures
        
        Args:
            hand_data: Hand information with gesture flags
        """
        current_time = time.time()
        is_pointing = hand_data.get('is_pointing', False)
        is_pinching = hand_data.get('is_pinching', False)
        is_peace = hand_data.get('is_peace', False)
        
        # Pinch = Drag (hold mouse button and move)
        if is_pinching:
            if not self.is_dragging:
                # Start dragging
                try:
                    pyautogui.mouseDown()
                    self.is_dragging = True
                    print("🖱️ Drag started")
                except Exception as e:
                    print(f"Error starting drag: {e}")
        else:
            if self.is_dragging:
                # Stop dragging
                try:
                    pyautogui.mouseUp()
                    self.is_dragging = False
                    print("🖱️ Drag ended")
                except Exception as e:
                    print(f"Error ending drag: {e}")
        
        # Pointing = Click (with cooldown to prevent spam)
        if is_pointing and not self.is_dragging:
            if current_time - self.last_click_time > self.click_cooldown:
                try:
                    pyautogui.click()
                    self.last_click_time = current_time
                    print("🖱️ Click!")
                except Exception as e:
                    print(f"Error clicking: {e}")
        
        # Peace sign = Right click
        if is_peace and not self.is_dragging:
            if current_time - self.last_click_time > self.click_cooldown:
                try:
                    pyautogui.rightClick()
                    self.last_click_time = current_time
                    print("🖱️ Right click!")
                except Exception as e:
                    print(f"Error right-clicking: {e}")
    
    def set_smooth_factor(self, factor: float):
        """
        Set cursor smoothing factor
        
        Args:
            factor: Smoothing factor (0.1 = very smooth, 1.0 = instant)
        """
        self.smooth_factor = np.clip(factor, 0.1, 1.0)
    
    def handle_scroll_gesture(self, hand_data: Dict):
        """
        Handle scroll gesture (two fingers together moving up/down)
        
        Args:
            hand_data: Hand information with gesture flags and position
        """
        is_two_fingers = hand_data.get('is_two_fingers', False)
        palm_y = hand_data['palm_position']['y']
        current_time = time.time()
        
        if is_two_fingers:
            if not self.is_scrolling:
                # Start scrolling
                self.is_scrolling = True
                self.last_scroll_y = palm_y
                self.last_scroll_time = current_time
            else:
                # Check if enough movement to scroll
                if current_time - self.last_scroll_time > self.scroll_cooldown:
                    y_diff = palm_y - self.last_scroll_y
                    
                    if abs(y_diff) > self.scroll_threshold:
                        # Determine scroll direction and amount
                        scroll_amount = int(abs(y_diff) * 10)  # Scale movement to scroll units
                        scroll_amount = min(scroll_amount, 20)  # Cap at reasonable amount
                        
                        if y_diff > 0:
                            # Hand moved down (y increases) = scroll down
                            pyautogui.scroll(-scroll_amount)
                            print(f"📜 Scrolled down {scroll_amount}")
                        else:
                            # Hand moved up (y decreases) = scroll up
                            pyautogui.scroll(scroll_amount)
                            print(f"📜 Scrolled up {scroll_amount}")
                        
                        self.last_scroll_y = palm_y
                        self.last_scroll_time = current_time
        else:
            # Stop scrolling
            if self.is_scrolling:
                self.is_scrolling = False
                self.last_scroll_y = None
    
    def cleanup(self):
        """Clean up - ensure mouse button is released"""
        if self.is_dragging:
            try:
                pyautogui.mouseUp()
            except:
                pass


if __name__ == "__main__":
    # Test the mouse controller
    print("Testing Mouse Controller...")
    print("This will move your mouse cursor!")
    print("Move mouse to screen corner to stop (FAILSAFE)")
    
    import cv2
    from hand_tracker import HandTracker
    
    tracker = HandTracker(max_hands=1)
    controller = MouseController()
    
    if not tracker.start_camera():
        print("Failed to start camera")
        exit(1)
    
    print("\nControls:")
    print("- Move hand = Move cursor")
    print("- Point (index finger) = Click")
    print("- Pinch (thumb + index) = Drag")
    print("- Peace sign = Right click")
    print("- Press 'q' to quit")
    
    try:
        while True:
            frame, hands_data = tracker.process_frame()
            
            if hands_data:
                # Use first detected hand
                controller.update_from_hand(hands_data[0])
                
                # Show gesture status on frame
                hand = hands_data[0]
                status = []
                if hand.get('is_pointing'): status.append("POINTING")
                if hand.get('is_pinching'): status.append("PINCHING")
                if hand.get('is_peace'): status.append("PEACE")
                
                if status:
                    cv2.putText(frame, " | ".join(status), (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            if frame is not None:
                cv2.imshow('Hand Control', frame)
            
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        controller.cleanup()
        tracker.cleanup()
        cv2.destroyAllWindows()
        print("Test complete!")

