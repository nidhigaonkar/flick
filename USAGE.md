# Flick - User Guide

## Gesture Controls

### Left Hand Controls (Scroll Only)

| Gesture | Control | Description |
|---------|---------|-------------|
| **1 Finger Extended + Move Up** | Scroll Up | Extend index finger and move hand upward |
| **2 Fingers Together + Move Down** | Scroll Down | Touch index & middle fingers together and move hand downward |

### Right Hand Controls

| Gesture | Control | Description |
|---------|---------|-------------|
| **X Position** (left/right) | Filter Amount | Adjust filter/effect intensity |
| **Y Position** (up/down) | Right Deck Volume | Raise hand = louder, lower hand = quieter |
| **Open Palm** | Play Right Deck | Spread fingers to play |
| **Closed Fist** | Pause Right Deck | Close hand to pause |

### Two-Hand Gestures

| Gesture | Control | Description |
|---------|---------|-------------|
| **Both Hands Pinching** | Toggle Effect | Pinch thumb and index finger on both hands to trigger FX |

## Tips for Best Results

### Hand Positioning

1. **Distance**: Keep hands 1-2 feet from camera
2. **Lighting**: Face a light source, avoid backlighting
3. **Background**: Plain, contrasting backgrounds work best
4. **Angle**: Keep palms facing camera

### Smooth Control

1. **Move Slowly**: Smooth, deliberate movements work better than jerky motions
2. **Hold Position**: When adjusting faders, hold position for a moment
3. **Calibrate**: Use sensitivity sliders to adjust to your style
4. **Practice**: Spend a few minutes getting comfortable with the mappings

### Performance Tips

1. **Pre-load Tracks**: Load tracks in YouDJ before starting gestures
2. **One Hand at a Time**: Master single-hand controls before combining
3. **Visual Feedback**: Watch the UI to see what gestures are detected
4. **Gesture Status**: Green "Detected" means your hand is being tracked

## UI Overview

### Main Window

```
┌─────────────────────────────────────────────────────┐
│  ✋ FLICK          ● STATUS         [START/STOP]    │
├────────────────────────┬────────────────────────────┤
│                        │  GESTURE STATUS            │
│   CAMERA FEED          │   Left Hand: ✅            │
│   (with hand           │   Right Hand: ✅           │
│    landmarks)          │   Crossfader: 0.50         │
│                        │   Volume L: 0.75           │
│                        │   Volume R: 0.60           │
│                        │   Filter: 0.45             │
│                        ├────────────────────────────┤
│                        │  SENSITIVITY               │
│                        │   Volume:     [===∎====]   │
│                        │   Crossfader: [===∎====]   │
│                        │   Filter:     [===∎====]   │
│                        ├────────────────────────────┤
│                        │  GESTURES                  │
│                        │   ✋ Left X → Crossfader   │
│                        │   📊 Hand Y → Volume       │
│                        │   ▶️  Open → Play          │
│                        │   ⏸️  Fist → Pause         │
│                        │   🎚️ Right X → Filter     │
│                        │   🤏 Pinch → Effect       │
└────────────────────────┴────────────────────────────┘
```

### Sensitivity Sliders

- **Volume**: Adjust how responsive volume control is to hand height
- **Crossfader**: Adjust how responsive crossfader is to hand position
- **Filter**: Adjust filter control sensitivity

Range: 0.5x (less sensitive) to 2.0x (more sensitive)

## Workflow Examples

### Basic Mixing

1. Start Flick and click START
2. Load a track in each deck on YouDJ
3. Use right hand Y-position to adjust right deck volume
4. Open right hand (palm) to play right deck
5. Use left hand X-position to crossfade between decks
6. Close left hand (fist) to pause left deck when transitioning

### Adding Effects

1. Position hands for normal mixing
2. When you want to trigger an effect, pinch both hands (thumb to index finger)
3. This will toggle the FX on/off
4. Continue mixing normally

### Volume Drops

1. Mix normally with both hands
2. To drop volume on a deck, quickly lower that hand
3. To bring it back, raise hand smoothly
4. Use fist gesture to cut immediately

## Troubleshooting

### Gestures Not Responding

- Check if hands show "✅ Detected" in status panel
- Ensure good lighting
- Try adjusting sensitivity sliders
- Make sure YouDJ page is loaded in browser

### Controls Too Sensitive

- Lower sensitivity sliders (below 1.0)
- Move hands more slowly
- Check camera isn't too close

### Controls Not Sensitive Enough

- Raise sensitivity sliders (above 1.0)
- Make larger hand movements
- Ensure full hand is in frame

### Browser Not Responding

- Check if YouDJ page is fully loaded
- Click anywhere on the YouDJ page to ensure it has focus
- Restart Flick if browser connection is lost

## Advanced Tips

### Custom Configuration

Edit `config.json` to customize:

```json
{
  "volume_sensitivity": 1.5,
  "crossfader_sensitivity": 1.0,
  "filter_sensitivity": 0.8,
  "gesture_smoothing": 3
}
```

### Performance Mode

For better performance on slower machines:

1. Close other applications
2. Reduce `gesture_smoothing` in config (faster but less smooth)
3. Ensure good lighting to improve detection speed

## Keyboard Shortcuts

While Flick is running:

- Browser window: Use YouDJ's built-in keyboard shortcuts
- Flick window: Use sensitivity sliders for real-time adjustment

## Best Practice Workflow

1. **Prepare**: Load tracks in YouDJ, adjust BPM sync
2. **Calibrate**: Start Flick, adjust sensitivity to your preference
3. **Test**: Practice gestures with music to get comfortable
4. **Perform**: Mix naturally, let your hands flow
5. **Save**: Flick auto-saves your sensitivity settings

---

**Have fun DJing with Flick!** 🎵✋

Remember: Practice makes perfect. The more you use it, the more natural gesture control will feel!

