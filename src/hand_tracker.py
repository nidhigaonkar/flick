"""
Hand Tracking Module
Uses MediaPipe Tasks API to detect and track hand landmarks from webcam feed
"""

import cv2
import numpy as np
from typing import Optional, Tuple, List, Dict

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
    
    # Try to import new Tasks API (required for MediaPipe 0.10.30+)
    try:
        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision
        TASKS_API_AVAILABLE = True
    except (ImportError, AttributeError):
        TASKS_API_AVAILABLE = False
    
    # Try to import old Solutions API (for MediaPipe < 0.10.30)
    SOLUTIONS_API_AVAILABLE = False
    try:
        if hasattr(mp, 'solutions'):
            from mediapipe import solutions
            SOLUTIONS_API_AVAILABLE = True
    except (ImportError, AttributeError):
        SOLUTIONS_API_AVAILABLE = False
        
except ImportError as e:
    MEDIAPIPE_AVAILABLE = False
    TASKS_API_AVAILABLE = False
    SOLUTIONS_API_AVAILABLE = False
    print(f"ERROR: MediaPipe is not installed correctly: {e}")
    print("Please run: pip install --upgrade mediapipe")


class HandTracker:
    """Tracks hands using MediaPipe Tasks API and provides landmark data"""
    
    def __init__(self, max_hands: int = 2, detection_confidence: float = 0.7, tracking_confidence: float = 0.7):
        """
        Initialize the hand tracker
        
        Args:
            max_hands: Maximum number of hands to detect (1 or 2)
            detection_confidence: Minimum confidence for detection
            tracking_confidence: Minimum confidence for tracking
        """
        if not MEDIAPIPE_AVAILABLE:
            raise ImportError(
                "MediaPipe is not installed or not working correctly.\n"
                "Please install it with: pip install --upgrade mediapipe\n"
                "Or if using a virtual environment, activate it first and then install."
            )
        
        # Determine which API to use
        self.use_tasks_api = False
        solutions_available = SOLUTIONS_API_AVAILABLE
        tasks_available = TASKS_API_AVAILABLE
        
        # Try old Solutions API first (works with mediapipe 0.10.8)
        if solutions_available and hasattr(mp, 'solutions'):
            try:
                self.mp_hands = mp.solutions.hands
                self.mp_drawing = mp.solutions.drawing_utils
                self.mp_drawing_styles = mp.solutions.drawing_styles
                
                self.hands = self.mp_hands.Hands(
                    max_num_hands=max_hands,
                    min_detection_confidence=detection_confidence,
                    min_tracking_confidence=tracking_confidence
                )
                self.use_tasks_api = False
                print("✅ Using MediaPipe Solutions API")
                return  # Successfully initialized, exit early
            except Exception as e:
                print(f"⚠️  Solutions API failed: {e}, trying Tasks API...")
                solutions_available = False
        
        # Fallback to new Tasks API (required for macOS with MediaPipe 0.10.30+)
        if not solutions_available and tasks_available:
            try:
                # Download or get the default hand landmarker model
                model_path = self._get_hand_landmarker_model()
                
                base_options = python.BaseOptions(model_asset_path=model_path)
                options = vision.HandLandmarkerOptions(
                    base_options=base_options,
                    num_hands=max_hands,
                    min_hand_detection_confidence=detection_confidence,
                    min_hand_presence_confidence=tracking_confidence,
                    min_tracking_confidence=tracking_confidence,
                    running_mode=vision.RunningMode.VIDEO
                )
                
                self.detector = vision.HandLandmarker.create_from_options(options)
                self.use_tasks_api = True
                print("✅ Using MediaPipe Tasks API (v0.10.30+)")
            except Exception as e:
                import traceback
                traceback.print_exc()
                raise ImportError(
                    f"❌ MediaPipe Tasks API failed: {e}\n\n"
                    "SOLUTION: Make sure MediaPipe is installed:\n"
                    "pip install mediapipe>=0.10.30"
                )
        
        if not solutions_available and not tasks_available:
            raise ImportError(
                "❌ No MediaPipe API available!\n\n"
                "SOLUTION: Install MediaPipe:\n"
                "pip install mediapipe>=0.10.30"
            )
        
        self.cap = None
        self.frame_width = 640
        self.frame_height = 480
        self.frame_timestamp_ms = 0
    
    def _get_hand_landmarker_model(self) -> str:
        """
        Get the path to the hand landmarker model file.
        Downloads it if necessary.
        
        Returns:
            Path to the model file
        """
        import os
        import urllib.request
        
        # Model URL from MediaPipe
        model_url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
        
        # Local cache directory
        cache_dir = os.path.join(os.path.expanduser("~"), ".flick_models")
        os.makedirs(cache_dir, exist_ok=True)
        
        model_path = os.path.join(cache_dir, "hand_landmarker.task")
        
        # Download if not exists
        if not os.path.exists(model_path):
            print("📥 Downloading hand landmarker model (one-time download)...")
            try:
                urllib.request.urlretrieve(model_url, model_path)
                print(f"✅ Model downloaded to: {model_path}")
            except Exception as e:
                raise ImportError(
                    f"Failed to download hand landmarker model: {e}\n"
                    "Please check your internet connection and try again."
                )
        
        return model_path
        
    def start_camera(self, camera_index: int = 0) -> bool:
        """
        Start the webcam capture
        
        Args:
            camera_index: Camera device index (0 for default)
            
        Returns:
            True if camera started successfully
        """
        self.cap = cv2.VideoCapture(camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        
        if not self.cap.isOpened():
            print("Error: Could not open camera")
            return False
        
        return True
    
    def stop_camera(self):
        """Release the camera"""
        if self.cap:
            self.cap.release()
            self.cap = None
    
    def process_frame(self) -> Tuple[Optional[np.ndarray], Optional[List[Dict]]]:
        """
        Capture and process a single frame
        
        Returns:
            Tuple of (frame, hands_data) where hands_data is a list of hand info dicts
        """
        if not self.cap or not self.cap.isOpened():
            return None, None
        
        success, frame = self.cap.read()
        if not success:
            return None, None
        
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        hands_data = []
        
        if self.use_tasks_api:
            # Use new Tasks API
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            # Process frame (VIDEO mode)
            self.frame_timestamp_ms += 33  # ~30 FPS
            detection_result = self.detector.detect_for_video(mp_image, self.frame_timestamp_ms)
            
            # Draw landmarks and extract data
            if detection_result.hand_landmarks:
                for idx, hand_landmarks in enumerate(detection_result.hand_landmarks):
                    # Draw landmarks
                    self._draw_landmarks(frame, hand_landmarks)
                    
                    # Get handedness (flip because camera is mirrored)
                    hand_label = "Right"  # Default
                    if detection_result.handedness and idx < len(detection_result.handedness):
                        handedness_list = detection_result.handedness[idx]
                        if handedness_list and len(handedness_list) > 0:
                            # Flip: camera's "Left" = user's right, camera's "Right" = user's left
                            mp_label = handedness_list[0].category_name
                            hand_label = "Right" if mp_label == "Left" else "Left"
                    
                    # Extract hand data
                    hand_info = self._extract_hand_info_tasks(hand_landmarks, hand_label)
                    hands_data.append(hand_info)
        else:
            # Use old Solutions API
            rgb_frame.flags.writeable = False
            results = self.hands.process(rgb_frame)
            rgb_frame.flags.writeable = True
            
            if results.multi_hand_landmarks and results.multi_handedness:
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                    # Draw landmarks on frame
                    self.mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style()
                    )
                    
                    # Extract hand data
                    hand_info = self._extract_hand_info(hand_landmarks, handedness)
                    hands_data.append(hand_info)
        
        return frame, hands_data
    
    def _draw_landmarks(self, frame: np.ndarray, landmarks):
        """Draw hand landmarks on frame (for Tasks API)"""
        h, w = frame.shape[:2]
        
        # Draw landmarks as circles
        for landmark in landmarks:
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
        
        # Draw connections (hand structure)
        # Hand connections: thumb, index, middle, ring, pinky
        connections = [
            # Thumb
            (0, 1), (1, 2), (2, 3), (3, 4),
            # Index finger
            (0, 5), (5, 6), (6, 7), (7, 8),
            # Middle finger
            (0, 9), (9, 10), (10, 11), (11, 12),
            # Ring finger
            (0, 13), (13, 14), (14, 15), (15, 16),
            # Pinky
            (0, 17), (17, 18), (18, 19), (19, 20),
            # Palm
            (5, 9), (9, 13), (13, 17)
        ]
        
        for start_idx, end_idx in connections:
            if start_idx < len(landmarks) and end_idx < len(landmarks):
                x1 = int(landmarks[start_idx].x * w)
                y1 = int(landmarks[start_idx].y * h)
                x2 = int(landmarks[end_idx].x * w)
                y2 = int(landmarks[end_idx].y * h)
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
    def _extract_hand_info_tasks(self, hand_landmarks, hand_label: str) -> Dict:
        """
        Extract useful information from hand landmarks (Tasks API)
        
        Args:
            hand_landmarks: MediaPipe hand landmarks from Tasks API
            hand_label: Hand label string ('Left' or 'Right')
            
        Returns:
            Dictionary with hand information
        """
        # Extract landmark positions (normalized 0-1)
        landmarks = []
        for lm in hand_landmarks:
            landmarks.append({
                'x': lm.x,
                'y': lm.y,
                'z': lm.z
            })
        
        # Calculate palm center (average of base landmarks)
        palm_landmarks = [0, 1, 5, 9, 13, 17]  # Wrist and base of each finger
        palm_x = np.mean([landmarks[i]['x'] for i in palm_landmarks])
        palm_y = np.mean([landmarks[i]['y'] for i in palm_landmarks])
        palm_z = np.mean([landmarks[i]['z'] for i in palm_landmarks])
        
        # Calculate if hand is open or closed (based on finger distances)
        is_open = self._is_hand_open(landmarks)
        
        # Calculate pinch gesture (thumb tip to index tip distance)
        # Only detect pinch for right hand (left hand is for scrolling only)
        is_pinching = self._is_pinching(landmarks) if hand_label == 'Right' else False
        
        # Calculate other gestures
        # Only detect pointing, peace, thumbs up for right hand (left hand is for scrolling)
        is_pointing = self._is_pointing(landmarks) if hand_label == 'Right' else False
        is_peace = self._is_peace_sign(landmarks) if hand_label == 'Right' else False
        is_thumbs_up = self._is_thumbs_up(landmarks) if hand_label == 'Right' else False
        is_two_fingers = self._is_two_fingers_together(landmarks)
        
        # Count extended fingers (for scroll gesture detection)
        extended_fingers = self._count_extended_fingers(landmarks)
        
        return {
            'label': hand_label,  # 'Left' or 'Right'
            'landmarks': landmarks,
            'palm_position': {'x': palm_x, 'y': palm_y, 'z': palm_z},
            'is_open': is_open,
            'is_pinching': is_pinching,
            'is_pointing': is_pointing,
            'is_peace': is_peace,
            'is_thumbs_up': is_thumbs_up,
            'is_two_fingers': is_two_fingers,
            'extended_fingers': extended_fingers
        }
    
    def _extract_hand_info(self, hand_landmarks, handedness) -> Dict:
        """
        Extract useful information from hand landmarks (Solutions API)
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
            handedness: MediaPipe handedness info
            
        Returns:
            Dictionary with hand information
        """
        # Get hand label (Left or Right) - flip because camera is mirrored
        mp_label = handedness.classification[0].label
        # Flip: camera's "Left" = user's right, camera's "Right" = user's left
        hand_label = "Right" if mp_label == "Left" else "Left"
        
        # Extract landmark positions (normalized 0-1)
        landmarks = []
        for lm in hand_landmarks.landmark:
            landmarks.append({
                'x': lm.x,
                'y': lm.y,
                'z': lm.z
            })
        
        # Calculate palm center (average of base landmarks)
        palm_landmarks = [0, 1, 5, 9, 13, 17]  # Wrist and base of each finger
        palm_x = np.mean([landmarks[i]['x'] for i in palm_landmarks])
        palm_y = np.mean([landmarks[i]['y'] for i in palm_landmarks])
        palm_z = np.mean([landmarks[i]['z'] for i in palm_landmarks])
        
        # Calculate if hand is open or closed (based on finger distances)
        is_open = self._is_hand_open(landmarks)
        
        # Calculate pinch gesture (thumb tip to index tip distance)
        # Only detect pinch for right hand (left hand is for scrolling only)
        is_pinching = self._is_pinching(landmarks) if hand_label == 'Right' else False
        
        # Calculate other gestures
        # Only detect pointing, peace, thumbs up for right hand (left hand is for scrolling)
        is_pointing = self._is_pointing(landmarks) if hand_label == 'Right' else False
        is_peace = self._is_peace_sign(landmarks) if hand_label == 'Right' else False
        is_thumbs_up = self._is_thumbs_up(landmarks) if hand_label == 'Right' else False
        is_two_fingers = self._is_two_fingers_together(landmarks)
        
        # Count extended fingers (for scroll gesture detection)
        extended_fingers = self._count_extended_fingers(landmarks)
        
        return {
            'label': hand_label,  # 'Left' or 'Right'
            'landmarks': landmarks,
            'palm_position': {'x': palm_x, 'y': palm_y, 'z': palm_z},
            'is_open': is_open,
            'is_pinching': is_pinching,
            'is_pointing': is_pointing,
            'is_peace': is_peace,
            'is_thumbs_up': is_thumbs_up,
            'is_two_fingers': is_two_fingers,
            'extended_fingers': extended_fingers
        }
    
    def _is_hand_open(self, landmarks: List[Dict]) -> bool:
        """
        Determine if hand is open (all fingers extended)
        
        Args:
            landmarks: List of landmark dictionaries
            
        Returns:
            True if hand is open
        """
        # Check if fingertips are far from palm
        fingertips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky tips
        palm_base = 0  # Wrist
        
        distances = []
        for tip_idx in fingertips:
            dist = np.sqrt(
                (landmarks[tip_idx]['x'] - landmarks[palm_base]['x']) ** 2 +
                (landmarks[tip_idx]['y'] - landmarks[palm_base]['y']) ** 2
            )
            distances.append(dist)
        
        avg_distance = np.mean(distances)
        
        # If average distance is above threshold, hand is open
        return avg_distance > 0.25
    
    def _is_pinching(self, landmarks: List[Dict]) -> bool:
        """
        Determine if thumb and index finger are pinching
        
        Args:
            landmarks: List of landmark dictionaries
            
        Returns:
            True if pinching
        """
        # Distance between thumb tip (4) and index tip (8)
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        
        distance = np.sqrt(
            (thumb_tip['x'] - index_tip['x']) ** 2 +
            (thumb_tip['y'] - index_tip['y']) ** 2
        )
        
        # If distance is small, they're pinching
        return distance < 0.05
    
    def _count_extended_fingers(self, landmarks: List[Dict]) -> int:
        """
        Count how many fingers are extended
        
        Args:
            landmarks: List of landmark dictionaries
            
        Returns:
            Number of extended fingers (0-5)
        """
        extended = 0
        
        # Finger tip and pip joint indices
        # Index: tip=8, pip=6
        # Middle: tip=12, pip=10
        # Ring: tip=16, pip=14
        # Pinky: tip=20, pip=18
        # Thumb: tip=4, ip=3
        
        fingers = [
            (8, 6),   # Index
            (12, 10), # Middle
            (16, 14), # Ring
            (20, 18), # Pinky
        ]
        
        # Check each finger (excluding thumb for now)
        for tip_idx, pip_idx in fingers:
            tip_y = landmarks[tip_idx]['y']
            pip_y = landmarks[pip_idx]['y']
            
            # If tip is above pip (lower y value), finger is extended
            if tip_y < pip_y - 0.03:  # Small threshold
                extended += 1
        
        # Check thumb separately (different geometry)
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        thumb_mcp = landmarks[2]
        
        # Thumb is extended if tip is far from hand base
        thumb_dist = np.sqrt(
            (thumb_tip['x'] - thumb_mcp['x']) ** 2 +
            (thumb_tip['y'] - thumb_mcp['y']) ** 2
        )
        if thumb_dist > 0.1:
            extended += 1
        
        return extended
    
    def _is_pointing(self, landmarks: List[Dict]) -> bool:
        """
        Determine if hand is pointing (index finger extended, others closed)
        
        Args:
            landmarks: List of landmark dictionaries
            
        Returns:
            True if pointing
        """
        # Check if index finger is extended
        index_extended = self._is_finger_extended(landmarks, 8, 6, 5)
        
        # Check if other fingers are closed
        middle_closed = not self._is_finger_extended(landmarks, 12, 10, 9)
        ring_closed = not self._is_finger_extended(landmarks, 16, 14, 13)
        pinky_closed = not self._is_finger_extended(landmarks, 20, 18, 17)
        
        return index_extended and middle_closed and ring_closed and pinky_closed
    
    def _is_peace_sign(self, landmarks: List[Dict]) -> bool:
        """
        Determine if hand is making peace sign (index and middle extended)
        
        Args:
            landmarks: List of landmark dictionaries
            
        Returns:
            True if peace sign
        """
        # Check if index and middle fingers are extended
        index_extended = self._is_finger_extended(landmarks, 8, 6, 5)
        middle_extended = self._is_finger_extended(landmarks, 12, 10, 9)
        
        # Check if other fingers are closed
        ring_closed = not self._is_finger_extended(landmarks, 16, 14, 13)
        pinky_closed = not self._is_finger_extended(landmarks, 20, 18, 17)
        
        return index_extended and middle_extended and ring_closed and pinky_closed
    
    def _is_two_fingers_together(self, landmarks: List[Dict]) -> bool:
        """
        Determine if index and middle fingertips are touching together (scroll gesture)
        
        Args:
            landmarks: List of landmark dictionaries
            
        Returns:
            True if two fingers touching
        """
        # Distance between index tip (8) and middle tip (12)
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        
        distance = np.sqrt(
            (index_tip['x'] - middle_tip['x']) ** 2 +
            (index_tip['y'] - middle_tip['y']) ** 2
        )
        
        # If distance is small, they're touching
        return distance < 0.05
    
    def _is_thumbs_up(self, landmarks: List[Dict]) -> bool:
        """
        Determine if hand is thumbs up (thumb extended, others closed)
        
        Args:
            landmarks: List of landmark dictionaries
            
        Returns:
            True if thumbs up
        """
        # Check if thumb is extended upward
        thumb_tip = landmarks[4]
        thumb_base = landmarks[2]
        wrist = landmarks[0]
        
        # Thumb tip should be higher (lower y) than thumb base and wrist
        thumb_extended = thumb_tip['y'] < thumb_base['y'] < wrist['y']
        
        # Check if other fingers are closed
        index_closed = not self._is_finger_extended(landmarks, 8, 6, 5)
        middle_closed = not self._is_finger_extended(landmarks, 12, 10, 9)
        ring_closed = not self._is_finger_extended(landmarks, 16, 14, 13)
        pinky_closed = not self._is_finger_extended(landmarks, 20, 18, 17)
        
        return thumb_extended and index_closed and middle_closed and ring_closed and pinky_closed
    
    def _is_finger_extended(self, landmarks: List[Dict], tip_idx: int, mid_idx: int, base_idx: int) -> bool:
        """
        Check if a specific finger is extended
        
        Args:
            landmarks: List of landmark dictionaries
            tip_idx: Index of fingertip
            mid_idx: Index of middle joint
            base_idx: Index of base joint
            
        Returns:
            True if finger is extended
        """
        # Calculate distance from tip to base
        tip = landmarks[tip_idx]
        base = landmarks[base_idx]
        
        distance = np.sqrt(
            (tip['x'] - base['x']) ** 2 +
            (tip['y'] - base['y']) ** 2
        )
        
        # If distance is large, finger is extended
        return distance > 0.15
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_camera()
        if self.use_tasks_api:
            if hasattr(self, 'detector'):
                self.detector.close()
        else:
            if hasattr(self, 'hands'):
                self.hands.close()


if __name__ == "__main__":
    # Test the hand tracker
    print("Testing Hand Tracker... Press 'q' to quit")
    
    tracker = HandTracker(max_hands=2)
    
    if not tracker.start_camera():
        print("Failed to start camera")
        exit(1)
    
    while True:
        frame, hands_data = tracker.process_frame()
        
        if frame is not None:
            # Display hand info on frame
            if hands_data:
                for i, hand in enumerate(hands_data):
                    text = f"{hand['label']} - Open: {hand['is_open']} Pinch: {hand['is_pinching']}"
                    cv2.putText(frame, text, (10, 30 + i * 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    palm = hand['palm_position']
                    pos_text = f"X: {palm['x']:.2f} Y: {palm['y']:.2f}"
                    cv2.putText(frame, pos_text, (10, 60 + i * 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            
            cv2.imshow('Flick Hand Tracker', frame)
        
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break
    
    tracker.cleanup()
    cv2.destroyAllWindows()
    print("Hand tracker test complete!")

