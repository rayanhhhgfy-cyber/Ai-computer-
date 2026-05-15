import cv2
import numpy as np
import pyautogui
from PIL import Image
import io
import base64

class VisionSystem:
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()

    def capture_screen(self, scale=0.5):
        """Captures the screen and returns it as a PIL image, optionally resized."""
        screenshot = pyautogui.screenshot()
        if scale != 1.0:
            new_size = (int(self.screen_width * scale), int(self.screen_height * scale))
            screenshot = screenshot.resize(new_size, Image.LANCZOS)
        return screenshot

    def get_base64_screenshot(self, scale=0.5, quality=80):
        """Returns the screenshot as a base64 encoded string for API consumption."""
        img = self.capture_screen(scale=scale)
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=quality)
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def save_screenshot(self, filename="last_screen.jpg", scale=1.0):
        img = self.capture_screen(scale=scale)
        img.save(filename)
        return filename

    def analyze_locally(self, image_path, model_path=None):
        """
        Placeholder for local vision analysis using Moondream or similar.
        In a real deployment, this would use llama-cpp-python's vision bindings.
        """
        # For now, this is a stub that would be filled by the actual local model runner
        return "Local vision analysis not yet fully implemented in this stub."

    def get_screen_info(self):
        return {
            "resolution": f"{self.screen_width}x{self.screen_height}",
            "aspect_ratio": self.screen_width / self.screen_height
        }

if __name__ == "__main__":
    vision = VisionSystem()
    print(f"Screen Info: {vision.get_screen_info()}")
    vision.save_screenshot("test_capture.jpg")
    print("Test screenshot saved.")
