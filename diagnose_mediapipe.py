#!/usr/bin/env python3
"""
Diagnostic script to check MediaPipe installation
"""

import sys

print("=" * 60)
print("MediaPipe Diagnostic Tool")
print("=" * 60)

# Check Python version
print(f"\nPython version: {sys.version}")
print(f"Python executable: {sys.executable}")

# Try importing MediaPipe
print("\n1. Checking MediaPipe import...")
try:
    import mediapipe as mp
    print("   ✅ MediaPipe imported successfully")
except ImportError as e:
    print(f"   ❌ Failed to import MediaPipe: {e}")
    print("\n   SOLUTION: Install MediaPipe with:")
    print("   pip install mediapipe")
    sys.exit(1)

# Check version
print("\n2. Checking MediaPipe version...")
try:
    version = mp.__version__
    print(f"   ✅ MediaPipe version: {version}")
except AttributeError:
    print("   ⚠️  No version attribute found")

# Check for solutions attribute
print("\n3. Checking for 'solutions' attribute...")
if hasattr(mp, 'solutions'):
    print("   ✅ 'solutions' attribute found")
    print(f"   Type: {type(mp.solutions)}")
    
    # Check for hands
    if hasattr(mp.solutions, 'hands'):
        print("   ✅ 'hands' found in solutions")
    else:
        print("   ❌ 'hands' NOT found in solutions")
        print(f"   Available in solutions: {[x for x in dir(mp.solutions) if not x.startswith('_')]}")
else:
    print("   ❌ 'solutions' attribute NOT found")
    print(f"   Available attributes: {[x for x in dir(mp) if not x.startswith('_')][:20]}")

# Check file location
print("\n4. Checking MediaPipe location...")
try:
    import os
    mp_file = mp.__file__
    print(f"   MediaPipe file: {mp_file}")
    print(f"   File exists: {os.path.exists(mp_file)}")
except AttributeError:
    print("   ⚠️  Could not determine file location")

# Check if it's a stub or actual package
print("\n5. Checking package integrity...")
try:
    # Try to access a known MediaPipe attribute
    if hasattr(mp, '__path__'):
        print(f"   Package path: {mp.__path__}")
    else:
        print("   ⚠️  Not a proper package")
except Exception as e:
    print(f"   ⚠️  Error checking package: {e}")

print("\n" + "=" * 60)
print("Diagnostic Complete")
print("=" * 60)

# Final recommendation
if not hasattr(mp, 'solutions'):
    print("\n❌ PROBLEM DETECTED: MediaPipe is installed but missing 'solutions'")
    print("\nSOLUTIONS TO TRY:")
    print("1. Reinstall MediaPipe:")
    print("   pip uninstall mediapipe")
    print("   pip install mediapipe")
    print("\n2. Try specific version:")
    print("   pip install mediapipe==0.10.8")
    print("\n3. Check for conflicts:")
    print("   pip list | grep mediapipe")
    print("\n4. If using virtual environment, make sure it's activated")
    print("   source venv/bin/activate")
else:
    print("\n✅ MediaPipe appears to be installed correctly!")
    print("   The issue might be elsewhere. Check the actual error message.")

