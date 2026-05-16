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

### 1. Computer Agent (PC)
1. **Install Python 3.10+**.
2. **Download the Repository** and go into the `pc_agent` folder.
3. **Run the Agent:**
   - Double-click `run_agent.bat`
   - It will install requirements and launch the interface.

### 2. Remote Control (iPhone / Vercel)
You can control the AI on your PC from your iPhone without installing anything.

#### A. Supabase Setup
- Create a free project on [Supabase](https://supabase.com).
- Create 3 tables (all lowercase):
  1. `logs`
     - `message` (text)
     - `created_at` (timestamptz, default: `now()`)
  2. `commands`
     - `id` (int8, primary key)
     - `instruction` (text)
     - `status` (text, e.g., 'pending')
     - `created_at` (timestamptz, default: `now()`)
  3. `state`
     - `id` (int8, primary key)
     - `last_screenshot` (text)
     - `updated_at` (timestamptz, default: `now()`)
- Get your `URL` and `Anon Key`.

#### B. Vercel Deployment
- Import this repository to Vercel.
- Vercel will use the `vercel.json` in the root to build the project.
- Add Environment Variables:
  - `NEXT_PUBLIC_SUPABASE_URL`
  - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- Password: `rayyan3mkidk`

#### C. PC Setup
- In the Peak AI UI, open "Remote Control" settings.
- Enter your Supabase URL and Key.
- Toggle "Enable Remote Control".
- Click "WAKE UP AGENT".

## For Developers: Building the .exe
1. Go into `pc_agent`.
2. Run `python scripts/build_exe.py`.
3. Find your `.exe` in the `dist/` folder.

## System Requirements
- **CPU:** i3 10th Gen+ (optimized for i3-10100).
- **RAM:** 8GB (Uses Phi-3/Moondream for offline).
- **OS:** Windows 10/11.
