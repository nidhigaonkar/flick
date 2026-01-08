# Flick Installation Guide

## Prerequisites

- Python 3.10 or higher
- Webcam
- Chrome browser
- macOS, Windows, or Linux

## Installation Steps

### 1. Install Python Dependencies

```bash
cd /Users/nidhigaonkar/Desktop/projects/flick
pip install -r requirements.txt
```

**Note:** The first time you run, it will automatically download the ChromeDriver for Selenium.

### 2. Test Your Setup

#### Test Hand Tracking (Optional)

```bash
python test_hand_tracking.py
```

This will open a window showing your webcam feed with hand detection. Press 'q' to quit.

#### Test Browser Controller (Optional)

```bash
python test_browser.py
```

This will open Chrome with YouDJ and test the automation controls.

### 3. Run Flick

```bash
python run.py
```

Or directly:

```bash
python src/main.py
```

## First Run

1. **Allow Camera Access**: Your system will ask for webcam permissions - click Allow
2. **Allow Browser Access**: Chrome will open and navigate to YouDJ
3. **Close Any Popups**: The app tries to auto-close YouDJ welcome dialogs, but you may need to manually accept terms
4. **Position Hands**: Place your hands in front of the camera
5. **Click START**: Begin controlling YouDJ with gestures!

## Troubleshooting

### Camera Not Working

- Check if another app is using your webcam
- Grant camera permissions in System Preferences (macOS) or Settings (Windows)
- Try changing the camera index in `config.json`

### Browser Controller Not Working

- Make sure Chrome is installed
- Check your internet connection (YouDJ requires internet)
- Try running `test_browser.py` to diagnose issues

### Hand Tracking Issues

- Ensure good lighting
- Keep hands within frame
- Avoid cluttered backgrounds
- Adjust detection confidence in settings

## Configuration

After first run, a `config.json` file will be created. You can edit this file to customize:

- Camera settings
- Sensitivity values
- Control mappings
- Browser options

## System Requirements

- **Minimum**: 
  - 4GB RAM
  - Dual-core processor
  - Basic webcam
  
- **Recommended**:
  - 8GB+ RAM
  - Quad-core processor
  - 720p+ webcam
  - Good lighting

## Need Help?

If you encounter issues:

1. Check the terminal output for error messages
2. Try the individual test scripts
3. Review the configuration file
4. Make sure all dependencies are installed correctly

Enjoy DJing with Flick! 🎵✋

