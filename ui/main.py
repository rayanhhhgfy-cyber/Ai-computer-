import flet as ft
import threading
import time
import os
from core.engine import AIEngine
from core.downloader import download_model, get_best_model_for_specs

def main(page: ft.Page):
    page.title = "Peak Reasoning AI Agent"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 500
    page.window_height = 800
    page.padding = 20

    # State variables
    engine = None
    running = False

    # UI Components
    title = ft.Text("AI System Controller", size=30, weight=ft.FontWeight.BOLD)

    api_key_input = ft.TextField(label="API Key (OpenAI/Groq/etc)", password=True, can_reveal_password=True)
    base_url_input = ft.TextField(label="Base URL (Optional)", value="https://api.openai.com/v1")
    model_input = ft.TextField(label="Model Name", value="gpt-4o")

    offline_toggle = ft.Switch(label="Offline Mode", value=False)

    status_text = ft.Text("Status: Standby", color=ft.colors.GREY_400)
    log_area = ft.ListView(expand=True, spacing=10, padding=10, auto_scroll=True)

    user_input = ft.TextField(label="Instructions for the AI", multiline=True, min_lines=2)

    def log(message, color=ft.colors.WHITE):
        log_area.controls.append(ft.Text(f"[{time.strftime('%H:%M:%S')}] {message}", color=color))
        page.update()

    def on_start_click(e):
        nonlocal engine, running

        if offline_toggle.value:
            model_path = "data/models/phi3.gguf"
            if not os.path.exists(model_path):
                log("Local model not found. Downloading 'Phi-3' (best for 8GB RAM)...", ft.colors.AMBER)
                llm_url, _ = get_best_model_for_specs()
                os.makedirs("data/models", exist_ok=True)
                if not download_model(llm_url, model_path):
                    log("Failed to download model.", ft.colors.RED)
                    return
                log("Download complete!", ft.colors.GREEN)

        if not offline_toggle.value and not api_key_input.value:
            log("Error: API Key required for online mode", ft.colors.RED)
            return

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
        offline_toggle.disabled = True
        status_text.value = "Status: ACTIVE (Watching Screen)"
        status_text.color = ft.colors.GREEN

        threading.Thread(target=agent_loop, daemon=True).start()
        page.update()

    def on_stop_click(e):
        nonlocal running
        running = False
        start_button.disabled = False
        stop_button.disabled = True
        offline_toggle.disabled = False
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
                response = engine.process_step(user_input=instruction)
                log(f"AI: {response}", ft.colors.CYAN_200)
                first_run = False
                time.sleep(2)
            except Exception as ex:
                log(f"Loop Error: {ex}", ft.colors.RED)
                running = False
                break

    start_button = ft.ElevatedButton("WAKE UP AGENT", on_click=on_start_click, icon=ft.icons.PLAY_ARROW)
    stop_button = ft.ElevatedButton("STOP AGENT", on_click=on_stop_click, icon=ft.icons.STOP, disabled=True)

    page.add(
        title,
        ft.Divider(),
        offline_toggle,
        api_key_input,
        base_url_input,
        model_input,
        ft.Row([start_button, stop_button]),
        status_text,
        ft.Divider(),
        user_input,
        ft.Text("Execution Log:"),
        ft.Container(
            content=log_area,
            border=ft.border.all(1, ft.colors.GREY_700),
            border_radius=10,
            height=300,
            expand=True
        ),
        ft.Text("Shortcut: Esc+Enter to Kill All Processes", size=12, color=ft.colors.RED_300)
    )

if __name__ == "__main__":
    ft.app(target=main)
