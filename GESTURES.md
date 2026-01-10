# Flick - Gesture Reference Guide

## 🖱️ MOUSE CONTROL MODE

Flick now controls your **system mouse cursor** directly! Your hand movements translate to mouse movements on screen, and gestures trigger clicks and drags. This lets you interact with YouDJ (or any application) naturally with your hands.

## How It Works

- **Move your hand** = Cursor moves on screen
- **Gestures** = Mouse actions (click, drag, right-click)
- **Camera window** = Shows your hand tracking (for fun!)
- **All actions happen** on the screen where you're looking

## Available Hand Gestures

### 🫳 Open Palm
**How to do it:** Spread all fingers wide  
**What it does:** 
- Normal cursor movement (no special action)
- Use this for moving around without clicking

### ✊ Closed Fist
**How to do it:** Close all fingers into a fist  
**What it does:**
- Normal cursor movement (no special action)
- Prevents accidental clicks

### 🤏 Pinch (Thumb + Index) - DRAG!
**How to do it:** Touch thumb tip to index finger tip  
**What it does:**
- **Click and hold** (mouse drag)
- Perfect for dragging sliders, crossfader, waveforms
- Move your hand while pinching to drag
- Release pinch to let go

### ✌️ Peace Sign - RIGHT CLICK!
**How to do it:** Extend index and middle fingers, keep others closed  
**What it does:**
- **Right click** at cursor position
- Opens context menus
- Useful for advanced controls

## 📜 LEFT HAND SCROLLING

The **left hand** is dedicated to scrolling. Use different finger counts to control scroll direction:

### 👆 1 Finger Extended - SCROLL UP
**How to do it:** Extend 1 finger on your LEFT hand  
**What it does:**
- **Scrolls up** continuously while finger is extended
- Perfect for scrolling through content upward
- Works on any webpage or application

### ✌️ 2 Fingers Extended - SCROLL DOWN
**How to do it:** Extend 2 fingers on your LEFT hand  
**What it does:**
- **Scrolls down** continuously while fingers are extended
- Perfect for scrolling through content downward
- Works on any webpage or application

**Note:** Left hand gestures (pinch, pointing, etc.) are disabled - left hand is for scrolling only!

## Hand Position = Cursor Position

Your hand position directly controls the mouse cursor:

- **Move hand LEFT** = Cursor moves LEFT
- **Move hand RIGHT** = Cursor moves RIGHT  
- **Move hand UP** = Cursor moves UP
- **Move hand DOWN** = Cursor moves DOWN

The cursor movement is **mirrored** for natural feel (like looking in a mirror).

### Tips for Precise Control

1. **Smoothing:** The cursor has built-in smoothing to prevent jitter
2. **Dead zone:** Very small movements are ignored for stability
3. **Speed:** Larger hand movements = faster cursor movement
4. **Position:** Keep hand 1-2 feet from camera for best tracking

## Tips for Best Control

### For Smooth Cursor Movement
1. **Steady hand:** Keep hand movement smooth and controlled
2. **Good lighting:** Ensure your hand is well-lit
3. **Solid background:** Plain background improves tracking
4. **Camera position:** Position camera at eye level
5. **Hand distance:** 1-2 feet from camera is optimal

### For Accurate Gestures
1. **Clear gestures:** Make distinct finger positions
2. **Hold briefly:** Hold gesture for a moment before releasing
3. **Cooldowns:** Gestures have cooldowns to prevent spam
4. **Practice:** Test each gesture before starting DJ session

### For DJing with YouDJ
1. **Open YouDJ** in browser first
2. **Click START** in Flick
3. **Move RIGHT hand** to position cursor over buttons/sliders
4. **Pinch and drag** for crossfader, volume, and waveform control
5. **Peace sign** (right hand) for context menus if needed
6. **Use LEFT hand** with 1-2 fingers to scroll up/down through tracks

## Safety Features

### FAILSAFE
- **Move mouse to screen corner** to instantly stop mouse control
- This is a built-in PyAutoGUI safety feature
- Use if cursor becomes unresponsive

### Cooldowns
- **Click cooldown:** 0.3 seconds between clicks
- Prevents accidental rapid clicking
- Makes gestures more intentional

### Drag Protection
- Drag only activates when pinching
- Releasing pinch immediately releases mouse button
- Prevents stuck drag states

## Adding Custom Actions

Want to add more functionality? The system is extensible:

1. **Edit `src/mouse_controller.py`** to add new gesture actions
2. **Edit `src/hand_tracker.py`** to add new gesture detection
3. **Thumbs up** is already detected and ready to map!

Example ideas:
- **Thumbs Up:** Double-click for loading tracks quickly
- **Thumbs Down:** Minimize/maximize window
- **Pointing gesture:** Left click (currently detected but not mapped)
- **Two hands:** Multi-touch gestures

## Troubleshooting

### Cursor is jumpy
- Increase smoothing in `mouse_controller.py` (lower `smooth_factor`)
- Improve lighting conditions
- Use a solid background

### Gestures not triggering
- Make gestures more distinct
- Hold gesture for longer
- Check cooldown hasn't activated
- Verify hand is fully visible to camera

### Cursor movement reversed
- This is intentional (mirrored mode)
- Edit `mouse_controller.py` line 47 to remove the flip

---

**Need help?** Check `USAGE.md` for general usage instructions or `README.md` for project overview.

