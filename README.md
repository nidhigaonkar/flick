# Flick ✋

**Control your computer with hand gestures!**

Flick is a computer vision-powered desktop app that lets you control your mouse cursor and scroll using hand gestures. No hardware needed - just your webcam.

## Features

- 🖐️ Real-time hand tracking with MediaPipe
- 🖱️ Control mouse cursor with hand movements
- 📜 Scroll with intuitive finger gestures
- 🖱️ Click and right-click with hand gestures
- 🎨 Visual feedback and gesture preview
- ⚙️ Customizable smoothing and sensitivity

## Gesture Controls

### Left Hand (Scroll Only)
| Gesture | Control |
|---------|---------|
| 1 Finger Extended + Move Up | Scroll Up |
| 1 Finger Extended + Move Down | Scroll Down |

### Right Hand (Mouse Control)
| Gesture | Control |
|---------|---------|
| Hand Movement | Move Cursor |
| Pinch (thumb + index) | Click & Drag |
| Peace Sign (✌️) | Right Click |

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run Flick:
```bash
python src/main.py
```

## Requirements

- Python 3.10+
- Webcam
- macOS, Windows, or Linux

## Usage

1. Launch Flick
2. Allow camera access
3. Position your hand in view
4. Start controlling your cursor!

## Tech Stack

- **Computer Vision**: MediaPipe, OpenCV
- **Mouse Control**: PyAutoGUI
- **UI**: Tkinter

---

*Control your computer naturally with hand gestures*
