#!/usr/bin/env python3
"""
Build standalone executable for Mimic using PyInstaller.

Usage:
    python build_executable.py

This creates a single executable file in dist/mimic that can be run
without Python installed.
"""

import subprocess
import sys
import platform
from pathlib import Path


def main():
    print("🔨 Building Mimic standalone executable...")
    print()

    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"✅ PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

    # Determine platform-specific options
    system = platform.system()
    exe_name = "mimic"

    if system == "Windows":
        exe_name = "mimic.exe"

    print(f"✅ Platform: {system}")
    print(f"✅ Output: dist/{exe_name}")
    print()

    # Build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # Single executable
        "--name", "mimic",              # Output name
        "--clean",                      # Clean build
        "--noconfirm",                  # Don't ask for confirmation
        # Hidden imports that PyInstaller might miss
        "--hidden-import", "pynput.keyboard._xorg",
        "--hidden-import", "pynput.mouse._xorg",
        "--hidden-import", "pynput.keyboard._win32",
        "--hidden-import", "pynput.mouse._win32",
        "--hidden-import", "pynput.keyboard._darwin",
        "--hidden-import", "pynput.mouse._darwin",
        "--hidden-import", "PIL.Image",
        "--hidden-import", "mss",
        "--hidden-import", "anthropic",
        # Entry point
        "mimic/main.py"
    ]

    print("🔧 Running PyInstaller...")
    print(f"   Command: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print()
        print("=" * 50)
        print("✅ Build successful!")
        print()
        print(f"📁 Executable location: dist/{exe_name}")
        print()
        print("To use:")
        if system == "Windows":
            print("   dist\\mimic.exe start my-task")
            print("   dist\\mimic.exe compile my-task")
        else:
            print("   ./dist/mimic start my-task")
            print("   ./dist/mimic compile my-task")
        print()
        print("To distribute:")
        print(f"   1. Copy dist/{exe_name} to target machine")
        print("   2. Set ANTHROPIC_API_KEY environment variable")
        print("   3. Run!")
        print("=" * 50)
    else:
        print()
        print("❌ Build failed. Check errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
