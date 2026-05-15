# Peak Reasoning AI Agent

A lightweight, autonomous AI agent that runs on your computer, sees your screen, and performs complex tasks for you.

## Features
- **Full Autonomous Control:** Moves mouse, types, and runs commands.
- **Screen Awareness:** "Watches" the screen to understand context.
- **Online & Offline Modes:** Use any API (OpenAI, Groq, etc.) or run locally (optimized for 8GB RAM).
- **Background/Foreground Modes:** Choose how the AI interacts.
- **Safety Kill Switch:** Press `Esc + Enter` to immediately stop all AI actions.
- **History:** Keeps track of your sessions.

## Setup Instructions

1. **Install Python 3.10+** (if not already installed).
2. **Clone/Download** this repository.
3. **Run the Agent:**
   - Double-click `run_agent.bat`
   - It will automatically install requirements and launch the interface.

## How to use
1. **Online Mode:**
   - Enter your API Key (e.g., from OpenAI, Groq, or OpenRouter).
   - Click "WAKE UP AGENT".
2. **Offline Mode:**
   - Toggle the "Offline Mode" switch.
   - The system will use local models (ensure you have enough disk space for initial downloads).
3. **Tasking:**
   - Type what you want the AI to do in the "Instructions" box.
   - Watch the execution log to see its "Thoughts" and "Actions".

## Remote Control (iPhone / Vercel)
You can control the AI on your PC from your iPhone without installing anything.

### 1. Supabase Setup
- Create a free project on [Supabase](https://supabase.com).
- Create 3 tables:
  1. `logs` (column: `message` text)
  2. `commands` (columns: `instruction` text, `status` text)
  3. `state` (columns: `id` int8 primary, `last_screenshot` text)
- Get your `URL` and `Anon Key`.

### 2. Vercel Deployment
- Import this repository to Vercel.
- **Important:** In Vercel Project Settings, set the **Root Directory** to `web_app`.
- Add Environment Variables:
  - `NEXT_PUBLIC_SUPABASE_URL`
  - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- Use the password: `rayyan3mkidk` on your iPhone.

### 3. PC Setup
- In the Peak AI UI, open "Remote Control" settings.
- Enter your Supabase URL and Key.
- Toggle "Enable Remote Control".
- Click "WAKE UP AGENT".

## For Developers: Building the .exe
If you want to bundle this into a single executable:
1. Open terminal in the project folder.
2. Run `python scripts/build_exe.py`.
3. Find your `.exe` in the `dist/` folder.

## System Requirements
- **CPU:** i3 10th Gen+ (optimized for i3-10100).
- **RAM:** 8GB (Uses lightweight models like Phi-3/Moondream for offline).
- **OS:** Windows 10/11.
