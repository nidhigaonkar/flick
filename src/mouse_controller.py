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
        self.last_click_time = 0
        self.click_cooldown = 0.3  # Seconds between clicks
        self.is_pinching = False  # Track pinch state for drag
        self.is_mouse_down = False  # Track if mouse button is held
        
        # Scroll state tracking
        self.is_scrolling = False
        self.scroll_cooldown = 0.05  # Seconds between scroll events (prevents scroll spam)
        self.last_scroll_time = 0
        
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
        # Direct mapping: hand right = cursor right, hand left = cursor left
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
        RIGHT HAND ONLY: Pinch to drag, Peace for right-click
        
        Args:
            hand_data: Hand information with gesture flags
        """
        current_time = time.time()
        is_pinching = hand_data.get('is_pinching', False)
        is_peace = hand_data.get('is_peace', False)
        
        # Pinch = Click and Drag (RIGHT HAND)
        if is_pinching:
            if not self.is_pinching:
                # Pinch just started - mouse down
                try:
                    pyautogui.mouseDown()
                    self.is_pinching = True
                    self.is_mouse_down = True
                    print("🖱️ Pinch - Mouse Down (start drag)")
                except Exception as e:
                    print(f"Error mouse down: {e}")
            # While pinching, cursor continues to move (handled in update_from_hand)
            # This allows dragging
        else:
            # Pinch ended - mouse up
            if self.is_pinching:
                try:
                    pyautogui.mouseUp()
                    self.is_pinching = False
                    self.is_mouse_down = False
                    print("🖱️ Pinch Released - Mouse Up (end drag)")
                except Exception as e:
                    print(f"Error mouse up: {e}")
        
        # Peace sign = Right click (only when not pinching)
        if not is_pinching and is_peace:
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
        Handle scroll gesture based on finger count
        - 1 finger extended = scroll up
        - 2 fingers extended = scroll down
        
        Args:
            hand_data: Hand information with gesture flags and position
        """
        extended_fingers = hand_data.get('extended_fingers', 0)
        current_time = time.time()
        
        # One or two fingers extended = scroll mode
        if extended_fingers == 1 or extended_fingers == 2:
            # Check if enough time has passed since last scroll
            if current_time - self.last_scroll_time >= self.scroll_cooldown:
                # Fixed scroll amount per gesture
                scroll_amount = 3  # Small, smooth scroll amount
                
                if extended_fingers == 1:
                    # 1 finger = scroll up
                    pyautogui.scroll(scroll_amount)
                    if not self.is_scrolling:
                        print(f"📜 ⬆️  Scroll UP mode (1 finger)")
                        self.is_scrolling = True
                elif extended_fingers == 2:
                    # 2 fingers = scroll down
                    pyautogui.scroll(-scroll_amount)
                    if not self.is_scrolling:
                        print(f"📜 ⬇️  Scroll DOWN mode (2 fingers)")
                        self.is_scrolling = True
                
                self.last_scroll_time = current_time
        else:
            # Stop scrolling if not one or two fingers
            if self.is_scrolling:
                self.is_scrolling = False
                print(f"📜 Scroll mode deactivated")
    
    def cleanup(self):
        """Clean up - ensure nothing stuck"""
        # Release mouse button if it's held down
        if self.is_mouse_down:
            try:
                pyautogui.mouseUp()
                self.is_mouse_down = False
                print("🛑 Released mouse button on cleanup")
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
    print("- Pinch (thumb + index) = Click & Drag")
    print("- Peace sign = Right click")
    print("- Left hand: 1 finger extended + move up/down = Scroll")
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
                if hand.get('is_pinching'): status.append("PINCHING (DRAG)")
                if hand.get('is_peace'): status.append("PEACE (RIGHT-CLICK)")
                
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

