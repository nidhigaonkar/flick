# Flick 

**Control your computer with hand gestures!**

Flick is a computer vision-powered app that lets you control your mouse cursor and scroll using hand gestures through real-time hand tracking with MediaPipe.

## Gesture Controls
Try them out while on this DJ website: https://youdj.online/ 

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

*DJ with the Air*
