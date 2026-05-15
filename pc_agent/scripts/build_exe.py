import os
import subprocess

def build():
    print("Starting Build Process...")

    # Check for PyInstaller
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.run(["pip", "install", "pyinstaller"])

    # Build command
    # --onefile: single exe
    # --noconsole: hide terminal
    # --name: set the output name

    cmd = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        "--name", "PeakReasoningAI",
        "--collect-all", "flet",
        "--hidden-import", "pywinauto",
        "--hidden-import", "pyautogui",
        "ui/main.py"
    ]

    print(f"Running command: {' '.join(cmd)}")
    print("Building executable...")
    # Attempt build if in appropriate environment (Windows usually required for .exe)
    if os.name == 'nt':
        subprocess.run(cmd)
    else:
        print("Non-Windows OS detected. Build skipped. Run this on Windows to get the .exe.")

if __name__ == "__main__":
    build()
