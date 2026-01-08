#!/usr/bin/env python3
"""
Test browser controller independently
"""

import sys
import os
import time

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from browser_controller import YouDJController

def main():
    print("=" * 50)
    print("Testing Browser Controller")
    print("=" * 50)
    print("\nThis will open a Chrome browser with YouDJ...")
    
    controller = YouDJController()
    
    if not controller.start(headless=False):
        print("❌ Failed to start browser controller")
        return 1
    
    print("✅ Browser started successfully!")
    print("\nTesting controls...\n")
    
    time.sleep(2)
    
    # Test crossfader
    print("Testing crossfader...")
    print("  Moving left (0.2)")
    controller.set_crossfader(0.2)
    time.sleep(1)
    
    print("  Moving center (0.5)")
    controller.set_crossfader(0.5)
    time.sleep(1)
    
    print("  Moving right (0.8)")
    controller.set_crossfader(0.8)
    time.sleep(1)
    
    print("  Back to center (0.5)")
    controller.set_crossfader(0.5)
    time.sleep(1)
    
    # Test volumes
    print("\nTesting volumes...")
    print("  Setting left volume to 0.8")
    controller.set_volume('left', 0.8)
    time.sleep(1)
    
    print("  Setting right volume to 0.6")
    controller.set_volume('right', 0.6)
    time.sleep(1)
    
    # Test filter
    print("\nTesting filter...")
    print("  Filter at 0.3")
    controller.set_filter(0.3)
    time.sleep(1)
    
    print("  Filter at 0.7")
    controller.set_filter(0.7)
    time.sleep(1)
    
    print("\n✅ All tests complete!")
    print("Browser will close in 5 seconds...")
    time.sleep(5)
    
    controller.stop()
    print("Browser closed.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

