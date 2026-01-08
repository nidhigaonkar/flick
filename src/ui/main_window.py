"""
Main UI Window
Desktop interface for Flick gesture controller
"""

import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import threading
from typing import Optional, Callable


class FlickUI:
    """Main UI window for Flick"""
    
    def __init__(self, on_start: Callable, on_stop: Callable, on_sensitivity_change: Callable):
        """
        Initialize the UI
        
        Args:
            on_start: Callback when start button is clicked
            on_stop: Callback when stop button is clicked
            on_sensitivity_change: Callback when sensitivity sliders change
        """
        self.on_start = on_start
        self.on_stop = on_stop
        self.on_sensitivity_change = on_sensitivity_change
        
        self.root = tk.Tk()
        self.root.title("Flick - Hand Gesture DJ Controller")
        self.root.geometry("900x700")
        self.root.configure(bg='#1a1a1a')
        
        # Status
        self.is_running = False
        self.current_frame = None
        
        # Build UI
        self._create_widgets()
        
    def _create_widgets(self):
        """Create all UI widgets"""
        
        # Top control panel
        control_frame = tk.Frame(self.root, bg='#2a2a2a', padx=10, pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)
        
        # Title
        title_label = tk.Label(
            control_frame,
            text="✋ FLICK",
            font=('Arial', 24, 'bold'),
            bg='#2a2a2a',
            fg='#00ff88'
        )
        title_label.pack(side=tk.LEFT, padx=10)
        
        # Status indicator
        self.status_label = tk.Label(
            control_frame,
            text="● STOPPED",
            font=('Arial', 12, 'bold'),
            bg='#2a2a2a',
            fg='#ff4444'
        )
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        # Start/Stop button
        self.start_button = tk.Button(
            control_frame,
            text="START",
            font=('Arial', 14, 'bold'),
            bg='#00ff88',
            fg='#000000',
            activebackground='#00cc66',
            command=self._toggle_start_stop,
            padx=30,
            pady=10
        )
        self.start_button.pack(side=tk.RIGHT, padx=10)
        
        # Main content area
        content_frame = tk.Frame(self.root, bg='#1a1a1a')
        content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side: Video feed
        video_frame = tk.Frame(content_frame, bg='#2a2a2a', padx=5, pady=5)
        video_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        video_label = tk.Label(
            video_frame,
            text="CAMERA FEED",
            font=('Arial', 10, 'bold'),
            bg='#2a2a2a',
            fg='#888888'
        )
        video_label.pack(side=tk.TOP, pady=5)
        
        # Video canvas
        self.video_canvas = tk.Label(
            video_frame,
            bg='#000000',
            width=640,
            height=480
        )
        self.video_canvas.pack(side=tk.TOP, padx=5, pady=5)
        
        # Right side: Controls and info
        right_frame = tk.Frame(content_frame, bg='#1a1a1a')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10)
        
        # Gesture status
        self._create_gesture_status(right_frame)
        
        # Sensitivity controls
        self._create_sensitivity_controls(right_frame)
        
        # Instructions
        self._create_instructions(right_frame)
        
    def _create_gesture_status(self, parent):
        """Create gesture status display"""
        status_frame = tk.LabelFrame(
            parent,
            text="GESTURE STATUS",
            font=('Arial', 10, 'bold'),
            bg='#2a2a2a',
            fg='#00ff88',
            padx=10,
            pady=10
        )
        status_frame.pack(side=tk.TOP, fill=tk.X, pady=10)
        
        # Gesture labels
        self.gesture_labels = {}
        
        gestures = [
            ('Left Hand', 'left_hand'),
            ('Right Hand', 'right_hand'),
            ('Gesture', 'crossfader'),
            ('Position X', 'volume_left'),
            ('Position Y', 'volume_right'),
            ('Mode', 'filter')
        ]
        
        for display_name, key in gestures:
            frame = tk.Frame(status_frame, bg='#2a2a2a')
            frame.pack(side=tk.TOP, fill=tk.X, pady=3)
            
            label = tk.Label(
                frame,
                text=f"{display_name}:",
                font=('Arial', 9),
                bg='#2a2a2a',
                fg='#cccccc',
                width=12,
                anchor='w'
            )
            label.pack(side=tk.LEFT)
            
            value_label = tk.Label(
                frame,
                text="--",
                font=('Arial', 9, 'bold'),
                bg='#2a2a2a',
                fg='#00ff88',
                width=15,
                anchor='w'
            )
            value_label.pack(side=tk.LEFT)
            
            self.gesture_labels[key] = value_label
    
    def _create_sensitivity_controls(self, parent):
        """Create sensitivity adjustment sliders"""
        sens_frame = tk.LabelFrame(
            parent,
            text="SENSITIVITY",
            font=('Arial', 10, 'bold'),
            bg='#2a2a2a',
            fg='#00ff88',
            padx=10,
            pady=10
        )
        sens_frame.pack(side=tk.TOP, fill=tk.X, pady=10)
        
        self.sensitivity_sliders = {}
        
        controls = [
            ('Smoothing', 'volume', 1.0),
        ]
        
        for display_name, key, default in controls:
            frame = tk.Frame(sens_frame, bg='#2a2a2a')
            frame.pack(side=tk.TOP, fill=tk.X, pady=5)
            
            label = tk.Label(
                frame,
                text=display_name,
                font=('Arial', 9),
                bg='#2a2a2a',
                fg='#cccccc',
                width=10,
                anchor='w'
            )
            label.pack(side=tk.LEFT)
            
            slider = tk.Scale(
                frame,
                from_=0.5,
                to=2.0,
                resolution=0.1,
                orient=tk.HORIZONTAL,
                bg='#2a2a2a',
                fg='#00ff88',
                highlightthickness=0,
                troughcolor='#444444',
                command=lambda val, k=key: self.on_sensitivity_change(k, float(val))
            )
            slider.set(default)
            slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            
            self.sensitivity_sliders[key] = slider
    
    def _create_instructions(self, parent):
        """Create instructions panel"""
        instr_frame = tk.LabelFrame(
            parent,
            text="GESTURES",
            font=('Arial', 10, 'bold'),
            bg='#2a2a2a',
            fg='#00ff88',
            padx=10,
            pady=10
        )
        instr_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=10)
        
        instructions = [
            "🖱️ Move Hand → Move Cursor",
            "👆 Point (Index) → Click",
            "🤏 Pinch → Click & Drag",
            "✌️ Peace Sign → Right Click",
            "🫳 Open Palm → Move Only",
            "✊ Closed Fist → Move Only"
        ]
        
        for instr in instructions:
            label = tk.Label(
                instr_frame,
                text=instr,
                font=('Arial', 9),
                bg='#2a2a2a',
                fg='#cccccc',
                anchor='w',
                pady=3
            )
            label.pack(side=tk.TOP, fill=tk.X)
    
    def _toggle_start_stop(self):
        """Handle start/stop button click"""
        if not self.is_running:
            self.is_running = True
            self.status_label.config(text="● RUNNING", fg='#00ff88')
            self.start_button.config(text="STOP", bg='#ff4444', activebackground='#cc0000')
            self.on_start()
        else:
            self.is_running = False
            self.status_label.config(text="● STOPPED", fg='#ff4444')
            self.start_button.config(text="START", bg='#00ff88', activebackground='#00cc66')
            self.on_stop()
    
    def update_video_frame(self, frame):
        """
        Update the video display with a new frame
        
        Args:
            frame: OpenCV frame (BGR)
        """
        if frame is not None:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Resize if needed
            rgb_frame = cv2.resize(rgb_frame, (640, 480))
            
            # Convert to PIL Image
            img = Image.fromarray(rgb_frame)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image=img)
            
            # Update canvas
            self.video_canvas.config(image=photo)
            self.video_canvas.image = photo  # Keep a reference
    
    def update_gesture_status(self, status_data: dict):
        """
        Update gesture status display
        
        Args:
            status_data: Dictionary with gesture status info
        """
        for key, value in status_data.items():
            if key in self.gesture_labels:
                self.gesture_labels[key].config(text=value)
    
    def run(self):
        """Start the UI main loop"""
        self.root.mainloop()
    
    def stop(self):
        """Stop the UI"""
        self.root.quit()
    
    def show_error(self, message: str):
        """Show an error message"""
        messagebox.showerror("Flick Error", message)
    
    def show_info(self, message: str):
        """Show an info message"""
        messagebox.showinfo("Flick", message)


if __name__ == "__main__":
    # Test the UI
    def on_start():
        print("Start button clicked!")
    
    def on_stop():
        print("Stop button clicked!")
    
    def on_sensitivity(control, value):
        print(f"Sensitivity changed: {control} = {value}")
    
    ui = FlickUI(on_start, on_stop, on_sensitivity)
    ui.run()

