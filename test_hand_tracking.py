#!/usr/bin/env python3
"""
Test hand tracking module independently
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from hand_tracker import HandTracker
import cv2

def main():
    print("=" * 50)
    print("Testing Hand Tracking Module")
    print("=" * 50)
    print("Press 'q' to quit\n")
    
    tracker = HandTracker(max_hands=2)
    
    if not tracker.start_camera():
        print("ERROR: Failed to start camera")
        return 1
    
    print("✅ Camera started successfully!")
    print("👋 Show your hands to the camera...")
    
    try:
        while True:
            frame, hands_data = tracker.process_frame()
            
            if frame is not None:
                # Display hand info
                if hands_data:
                    for i, hand in enumerate(hands_data):
                        y_pos = 30 + i * 80
                        
                        # Hand label
                        cv2.putText(
                            frame, 
                            f"{hand['label']} Hand Detected",
                            (10, y_pos), 
                            cv2.FONT_HERSHEY_SIMPLEX, 
                            0.7, 
                            (0, 255, 0), 
                            2
                        )
                        
                        # Palm position
                        palm = hand['palm_position']
                        cv2.putText(
                            frame,
                            f"Position: X={palm['x']:.2f} Y={palm['y']:.2f}",
                            (10, y_pos + 25),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (255, 255, 0),
                            1
                        )
                        
                        # Gestures
                        gestures = []
                        if hand['is_open']:
                            gestures.append("Open")
                        else:
                            gestures.append("Closed")
                        if hand['is_pinching']:
                            gestures.append("Pinching")
                        
                        cv2.putText(
                            frame,
                            f"Gestures: {', '.join(gestures)}",
                            (10, y_pos + 50),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (0, 255, 255),
                            1
                        )
                else:
                    cv2.putText(
                        frame,
                        "No hands detected",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2
                    )
                
                cv2.imshow('Flick Hand Tracking Test', frame)
            
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        tracker.cleanup()
        cv2.destroyAllWindows()
    
    print("\n✅ Hand tracking test complete!")
    return 0

if __name__ == "__main__":
    sys.exit(main())

