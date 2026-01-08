# Flick 🎵✋

**Control YouDJ with hand gestures!**

Flick is a computer vision-powered desktop app that lets you DJ using hand gestures. No hardware controller needed - just your webcam and some sick moves.

## Features

- 🖐️ Real-time hand tracking with MediaPipe
- 🎛️ Control crossfader, volume, effects with gestures
- 🌐 Automated browser control for YouDJ.online
- 🎨 Visual feedback and gesture preview
- ⚙️ Customizable gesture mappings

## Gesture Controls

| Gesture | Control |
|---------|---------|
| Left Hand X-Position | Crossfader |
| Hand Y-Position | Volume/Channel Faders |
| Open Palm | Play |
| Closed Fist | Pause |
| Pinch | Toggle Effects |

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
- Chrome browser

## Usage

1. Launch Flick
2. Allow camera access
3. Position your hands in view
4. Start mixing!

## Tech Stack

- **Computer Vision**: MediaPipe, OpenCV
- **Browser Automation**: Selenium
- **UI**: Tkinter

---

*Built with ❤️ for DJs who like to keep their hands free*

