import flet as ft
import threading
import time
import os
from core.engine import AIEngine
from core.downloader import download_model, get_best_model_for_specs
from core.remote import SupabaseBridge

def main(page: ft.Page):
    page.title = "Peak Reasoning AI Agent"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 500
    page.window_height = 900
    page.padding = 20
    page.scroll = ft.ScrollMode.ADAPTIVE

    # State variables
    engine = None
    running = False
    remote_bridge = None
    remote_running = False

    # UI Components
    title = ft.Text("AI System Controller", size=30, weight=ft.FontWeight.BOLD)

    api_key_input = ft.TextField(label="API Key (OpenAI/Groq/etc)", password=True, can_reveal_password=True)
    base_url_input = ft.TextField(label="Base URL (Optional)", value="https://api.openai.com/v1")
    model_input = ft.TextField(label="Model Name", value="gpt-4o")

    offline_toggle = ft.Switch(label="Offline Mode", value=False)

    # Remote Bridge Config
    remote_url = ft.TextField(label="Supabase URL", value="")
    remote_key = ft.TextField(label="Supabase Key", password=True, can_reveal_password=True)
    remote_toggle = ft.Switch(label="Enable Remote Control (iPhone)", value=False)

    status_text = ft.Text("Status: Standby", color=ft.colors.GREY_400)
    log_area = ft.ListView(expand=True, spacing=10, padding=10, auto_scroll=True)

    user_input = ft.TextField(label="Instructions for the AI", multiline=True, min_lines=2)

    def log(message, color=ft.colors.WHITE):
        log_area.controls.append(ft.Text(f"[{time.strftime('%H:%M:%S')}] {message}", color=color))
        if remote_bridge:
            threading.Thread(target=remote_bridge.post_log, args=(message,), daemon=True).start()
        page.update()

    def on_start_click(e):
        nonlocal engine, running, remote_bridge, remote_running

        if offline_toggle.value:
            llm_path = "data/models/phi3.gguf"
            vision_path = "data/models/moondream.gguf"
            if not os.path.exists(llm_path) or not os.path.exists(vision_path):
                log("Local models not found. Downloading 'Phi-3' & 'Moondream'...", ft.colors.AMBER)
                llm_url, vision_url = get_best_model_for_specs()
                os.makedirs("data/models", exist_ok=True)
                download_model(llm_url, llm_path)
                download_model(vision_url, vision_path)
                log("Downloads complete!", ft.colors.GREEN)

        if not offline_toggle.value and not api_key_input.value:
            log("Error: API Key required for online mode", ft.colors.RED)
            return

        if remote_toggle.value:
            if not remote_url.value or not remote_key.value:
                log("Error: Supabase credentials required for Remote", ft.colors.RED)
                return
            remote_bridge = SupabaseBridge(remote_url.value, remote_key.value)
            remote_running = True
            threading.Thread(target=remote_poll_loop, daemon=True).start()
            log("Remote Sync Active.")

        log("Initializing AI Engine...")
        engine = AIEngine(
            api_key=api_key_input.value,
            base_url=base_url_input.value,
            model=model_input.value,
            offline_mode=offline_toggle.value
        )

        running = True
        start_button.disabled = True
        stop_button.disabled = False
        status_text.value = "Status: ACTIVE (Watching Screen)"
        status_text.color = ft.colors.GREEN

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
        status_text.color = ft.colors.GREY_400
        log("Agent Stopped.")
        page.update()

    def agent_loop():
        nonlocal running
        first_run = True
        while running:
            try:
                instruction = user_input.value if first_run else None
                if instruction:
                    user_input.value = ""

                response = engine.process_step(user_input=instruction)
                log(f"AI: {response}", ft.colors.CYAN_200)
                first_run = False
                time.sleep(3)
            except Exception as ex:
                log(f"Loop Error: {ex}", ft.colors.RED)
                running = False
                break

    def remote_poll_loop():
        while remote_running:
            try:
                cmd = remote_bridge.get_latest_command()
                if cmd:
                    log(f"Remote Command Received: {cmd['instruction']}", ft.colors.AMBER)
                    user_input.value = cmd['instruction']
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

    start_button = ft.ElevatedButton("WAKE UP AGENT", on_click=on_start_click, icon=ft.icons.PLAY_ARROW)
    stop_button = ft.ElevatedButton("STOP AGENT", on_click=on_stop_click, icon=ft.icons.STOP, disabled=True)

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
                ft.Text("Password: rayyan3mkidk", size=12, color=ft.colors.GREY_500)
            ]
        ),
        ft.Row([start_button, stop_button]),
        status_text,
        ft.Divider(),
        user_input,
        ft.Text("Execution Log:"),
        ft.Container(
            content=log_area,
            border=ft.border.all(1, ft.colors.GREY_700),
            border_radius=10,
            height=250,
        ),
        ft.Text("Shortcut: Esc+Enter to Kill All Processes", size=12, color=ft.colors.RED_300)
    )

if __name__ == "__main__":
    ft.app(target=main)
