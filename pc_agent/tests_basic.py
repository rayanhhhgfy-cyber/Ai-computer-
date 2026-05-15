import unittest
from core.vision import VisionSystem
from core.controller import ComputerController
import os

class TestCoreModules(unittest.TestCase):
    def test_vision_init(self):
        vision = VisionSystem()
        self.assertIsNotNone(vision.get_screen_info())

    def test_controller_init(self):
        controller = ComputerController()
        self.assertFalse(controller.panic_triggered)

if __name__ == "__main__":
    unittest.main()
