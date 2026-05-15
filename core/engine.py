import os
import json
import time
import re
import pyautogui
from openai import OpenAI
from core.vision import VisionSystem
from core.controller import ComputerController

# Attempt to import llama-cpp for offline mode
try:
    from llama_cpp import Llama
    from llama_cpp.llama_chat_format import MoondreamChatHandler
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False

class AIEngine:
    def __init__(self, api_key=None, base_url=None, model="gpt-4o", offline_mode=False):
        self.offline_mode = offline_mode
        self.vision = VisionSystem()
        self.controller = ComputerController()
        self.screen_width, self.screen_height = pyautogui.size()
        self.history_file = "data/history/session.json"
        self.history = self._load_history()

        if not offline_mode:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
            self.model = model
        else:
            if LLAMA_AVAILABLE:
                llm_path = "data/models/phi3.gguf"
                vision_path = "data/models/moondream.gguf"
                if os.path.exists(llm_path) and os.path.exists(vision_path):
                    chat_handler = MoondreamChatHandler(model_path=vision_path)
                    self.local_llm = Llama(
                        model_path=llm_path,
                        chat_handler=chat_handler,
                        n_ctx=2048,
                        n_threads=4
                    )
                else:
                    print(f"Warning: Local models missing.")
                    self.local_llm = None
            else:
                self.local_llm = None
            self.model = "local-phi3-vision"

    def _load_history(self):
        os.makedirs("data/history", exist_ok=True)
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def _save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f)

    def get_system_prompt(self):
        return f"""You are an autonomous AI Agent with full control over the user's computer.
The screen resolution is {self.screen_width}x{self.screen_height}.
Your goal is to assist the user by performing complex tasks directly on their machine.
You can see the user's screen through screenshots.

Actions you can take:
- MOVE_MOUSE(x,y): Move mouse to absolute coordinates.
- CLICK(x,y): Click at coordinates.
- TYPE("text"): Type text.
- PRESS("key"): Press a keyboard key.
- RUN_CMD("command"): Run a shell command.
- BG_CLICK("window_title", "button_text"): Click a button in a specific window in the background.

Response format:
THOUGHT: (Your reasoning)
ACTION: (The action to take)
WAIT: (Seconds to wait)

If finished, end with "TASK_COMPLETE".
"""

    def process_step(self, user_input=None):
        # We scale to 0.5 for the AI, so the AI needs to know the true resolution
        screenshot_b64 = self.vision.get_base64_screenshot(scale=0.5)

        if self.offline_mode:
            if not self.local_llm:
                return "Error: Local models missing or llama-cpp not installed."

            response = self.local_llm.create_chat_completion(
                messages=[
                    {"role": "system", "content": self.get_system_prompt()},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_input or "Continue the task."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{screenshot_b64}"}}
                        ]
                    }
                ],
                max_tokens=200
            )
            content = response['choices'][0]['message']['content']
            self._parse_and_execute(content)
            return content

        messages = [{"role": "system", "content": self.get_system_prompt()}]
        messages.extend(self.history[-10:])

        if user_input:
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": user_input},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{screenshot_b64}"}}
                ]
            })
        else:
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": "Observe the current screen and continue the task."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{screenshot_b64}"}}
                ]
            })

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500
            )
            content = response.choices[0].message.content
            self.history.append({"role": "user", "content": "Visual context updated."})
            self.history.append({"role": "assistant", "content": content})
            self._save_history()

            self._parse_and_execute(content)
            return content
        except Exception as e:
            return f"Error: {str(e)}"

    def _parse_and_execute(self, content):
        # Extract actions
        actions = re.findall(r'ACTION:\s*(\w+)\((.*?)\)', content)
        for action_name, args in actions:
            try:
                # Clean args
                clean_args = [a.strip().strip('"').strip("'") for a in args.split(',')]

                if action_name == "MOVE_MOUSE":
                    x, y = map(int, clean_args)
                    self.controller.move_mouse(x, y)
                elif action_name == "CLICK":
                    if len(clean_args) == 2:
                        x, y = map(int, clean_args)
                        self.controller.click(x, y)
                    else:
                        self.controller.click()
                elif action_name == "TYPE":
                    self.controller.type_text(clean_args[0])
                elif action_name == "PRESS":
                    self.controller.press_key(clean_args[0])
                elif action_name == "RUN_CMD":
                    self.controller.run_command(clean_args[0])
                elif action_name == "BG_CLICK":
                    win_title, btn_text = clean_args
                    self.controller.interact_with_window(win_title, "click", btn_text)
            except Exception as e:
                print(f"Failed to execute {action_name}: {e}")

        wait_match = re.search(r'WAIT:\s*(\d+)', content)
        if wait_match:
            time.sleep(int(wait_match.group(1)))
