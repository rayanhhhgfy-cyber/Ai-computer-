import sys
import os

# Add the parent directory (pc_agent) to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import flet as ft
import threading
import time
from core.engine import AIEngine
from core.downloader import download_model, get_best_model_for_specs
from core.remote import SupabaseBridge

def main(page: ft.Page):
    page.title = "Peak Reasoning AI Agent"
    page.theme_mode = "dark"
    page.window_width = 500
    page.window_height = 900
    page.padding = 20
    page.scroll = "adaptive"

    # State variables
    engine = None
    running = False
    remote_bridge = None
    remote_running = False
    current_instruction = None

    # UI Components
    title = ft.Text("AI System Controller", size=30, weight="bold")

    api_key_input = ft.TextField(label="API Key (OpenAI/Groq/etc)", password=True, can_reveal_password=True)
    base_url_input = ft.TextField(label="Base URL (Optional)", value="https://api.openai.com/v1")
    model_input = ft.TextField(label="Model Name", value="gpt-4o")

    offline_toggle = ft.Switch(label="Offline Mode", value=False)

    # Remote Bridge Config
    remote_url = ft.TextField(label="Supabase URL", value="")
    remote_key = ft.TextField(label="Supabase Key", password=True, can_reveal_password=True)
    remote_toggle = ft.Switch(label="Enable Remote Control (iPhone)", value=False)

    status_text = ft.Text("Status: Standby", color="grey")
    log_area = ft.ListView(expand=True, spacing=10, padding=10, auto_scroll=True)

    user_input = ft.TextField(label="Instructions for the AI", multiline=True, min_lines=2)

    def log(message, color="white"):
        log_area.controls.append(ft.Text(f"[{time.strftime('%H:%M:%S')}] {message}", color=color))
        if remote_bridge:
            threading.Thread(target=remote_bridge.post_log, args=(message,), daemon=True).start()
        page.update()

    def on_start_click(e):
        nonlocal engine, running, remote_bridge, remote_running

        if offline_toggle.value:
            llm_path = os.path.join(parent_dir, "data", "models", "phi3.gguf")
            vision_path = os.path.join(parent_dir, "data", "models", "moondream.gguf")
            if not os.path.exists(llm_path) or not os.path.exists(vision_path):
                log("Local models missing. Downloading...", "amber")
                llm_url, vision_url = get_best_model_for_specs()
                os.makedirs(os.path.join(parent_dir, "data", "models"), exist_ok=True)
                threading.Thread(target=run_downloads, args=(llm_url, llm_path, vision_url, vision_path), daemon=True).start()
                return

        start_agent_logic()

    def run_downloads(l_url, l_path, v_url, v_path):
        download_model(l_url, l_path)
        download_model(v_url, v_path)
        log("Downloads complete! Click Wake Up again.", "green")

    def start_agent_logic():
        nonlocal engine, running, remote_bridge, remote_running
        if not offline_toggle.value and not api_key_input.value:
            log("Error: API Key required", "red")
            return

        if remote_toggle.value:
            if not remote_url.value or not remote_key.value:
                log("Error: Supabase credentials required", "red")
                return
            remote_bridge = SupabaseBridge(remote_url.value, remote_key.value)
            remote_running = True
            threading.Thread(target=remote_poll_loop, daemon=True).start()

        engine = AIEngine(
            api_key=api_key_input.value,
            base_url=base_url_input.value,
            model=model_input.value,
            offline_mode=offline_toggle.value
        )

        running = True
        start_button.disabled = True
        stop_button.disabled = False
        status_text.value = "Status: ACTIVE"
        status_text.color = "green"

        threading.Thread(target=agent_loop, daemon=True).start()
        if remote_bridge:
            threading.Thread(target=screenshot_sync_loop, daemon=True).start()
        page.update()

    def on_stop_click(e):
        nonlocal running, remote_running
        running = False
        remote_running = False
        start_button.disabled = False
        stop_button.disabled = True
        status_text.value = "Status: Standby"
        status_text.color = "grey"
        log("Agent Stopped.")
        page.update()

    def agent_loop():
        nonlocal running, current_instruction
        while running:
            try:
                if user_input.value:
                    current_instruction = user_input.value
                    user_input.value = ""
                    page.update()

                response = engine.process_step(user_input=current_instruction)
                log(f"AI: {response}", "cyan")

                current_instruction = None
                time.sleep(3)
            except Exception as ex:
                log(f"Loop Error: {ex}", "red")
                running = False
                break

    def remote_poll_loop():
        nonlocal current_instruction
        while remote_running:
            try:
                cmd = remote_bridge.get_latest_command()
                if cmd:
                    log(f"Remote Command: {cmd['instruction']}", "amber")
                    current_instruction = cmd['instruction']
                    remote_bridge.update_command_status(cmd['id'])
            except: pass
            time.sleep(5)

    def screenshot_sync_loop():
        while remote_running:
            if engine:
                try:
                    b64 = engine.vision.get_base64_screenshot(scale=0.3, quality=50)
                    remote_bridge.send_screenshot(b64)
                except: pass
            time.sleep(10)

    start_button = ft.ElevatedButton("WAKE UP AGENT", on_click=on_start_click, icon="PLAY_ARROW")
    stop_button = ft.ElevatedButton("STOP AGENT", on_click=on_stop_click, icon="STOP", disabled=True)

    page.add(
        title,
        ft.Divider(),
        ft.ExpansionTile(
            title=ft.Text("Connection Settings"),
            controls=[
                offline_toggle,
                api_key_input,
                base_url_input,
                model_input,
            ]
        ),
        ft.ExpansionTile(
            title=ft.Text("Remote Control (iPhone / Vercel)"),
            controls=[
                remote_toggle,
                remote_url,
                remote_key,
                ft.Text("Password: rayyan3mkidk", size=12, color="grey")
            ]
        ),
        ft.Row([start_button, stop_button]),
        status_text,
        ft.Divider(),
        user_input,
        ft.Text("Execution Log:"),
        ft.Container(
            content=log_area,
            border=ft.border.all(1, "grey"),
            border_radius=10,
            height=250,
        ),
        ft.Text("Shortcut: Esc+Enter to Kill All Processes", size=12, color="red")
    )

if __name__ == "__main__":
    print("Starting Peak AI UI...")
    # Use explicit target to be safe
    try:
        # Launching in web browser mode by default to avoid Windows Desktop initialization hangs
        ft.app(target=main, view=ft.AppView.WEB_BROWSER)
    except Exception as e:
        print(f"Error: {e}")
        # Final fallback
        ft.app(target=main)
