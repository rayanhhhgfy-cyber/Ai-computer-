import pyautogui
import pywinauto
import keyboard
import time
import sys
import threading
from pywinauto import Desktop

class ComputerController:
    def __init__(self):
        # Fail-safe: move mouse to corner to abort (pyautogui default)
        pyautogui.FAILSAFE = True
        self.panic_triggered = False
        self._setup_panic_button()

    def _setup_panic_button(self):
        """Sets up a global hotkey to stop all actions."""
        def trigger_panic():
            print("PANIC BUTTON TRIGGERED! Stopping all actions...")
            self.panic_triggered = True
            # Forcing exit might be too much, but we want to stop loops

        # Listening for Esc+Enter as requested
        keyboard.add_hotkey('esc+enter', trigger_panic)

    def check_panic(self):
        if self.panic_triggered:
            raise InterruptedError("Panic button pressed. Operation aborted.")

    # --- Foreground Controls ---

    def move_mouse(self, x, y):
        self.check_panic()
        pyautogui.moveTo(x, y, duration=0.5)

    def click(self, x=None, y=None, button='left'):
        self.check_panic()
        if x is not None and y is not None:
            pyautogui.click(x, y, button=button)
        else:
            pyautogui.click(button=button)

    def type_text(self, text):
        self.check_panic()
        pyautogui.write(text, interval=0.05)

    def press_key(self, key):
        self.check_panic()
        pyautogui.press(key)

    # --- Background (UI Automation) Controls ---

    def get_windows(self):
        """Returns a list of visible window titles."""
        windows = Desktop(backend="uia").windows()
        return [w.window_text() for w in windows if w.window_text()]

    def interact_with_window(self, title_query, action, value=None):
        """
        Sophisticated background interaction.
        action: 'click', 'type', 'select'
        """
        self.check_panic()
        try:
            app = pywinauto.Application(backend="uia").connect(title_re=f".*{title_query}.*", timeout=5)
            win = app.window(title_re=f".*{title_query}.*")
            win.set_focus() # Still brings to focus but doesn't necessarily move mouse

            if action == 'type':
                win.type_keys(value, with_spaces=True)
            elif action == 'click':
                # Attempt to find the specific element if value is provided
                if value:
                    win.child_window(title=value).click_input()
                else:
                    win.click_input()
            return True
        except Exception as e:
            print(f"Error interacting with window: {e}")
            return False

    def run_command(self, command):
        """Runs a terminal command."""
        self.check_panic()
        import subprocess
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.stdout or result.stderr
        except Exception as e:
            return str(e)

if __name__ == "__main__":
    # Test script
    controller = ComputerController()
    print("Controller initialized. Press Esc+Enter to test panic.")
    try:
        while True:
            time.sleep(1)
            if controller.panic_triggered:
                break
    except KeyboardInterrupt:
        pass
