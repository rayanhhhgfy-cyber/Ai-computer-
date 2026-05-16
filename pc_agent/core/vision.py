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

    def get_screen_info(self):
        return {
            "resolution": f"{self.screen_width}x{self.screen_height}",
            "aspect_ratio": self.screen_width / self.screen_height
        }
