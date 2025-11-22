# 🤖 Claude Jarvis

Turn your Claude Desktop into a **Jarvis-like assistant** capable of controlling your Windows PC.

This Model Context Protocol (MCP) server gives Claude "hands" and "eyes" to interact with your local environment, automating tasks ranging from system monitoring to complex workflows.

## ✨ Features

### 🧠 Phase 1: The Foundation
- **System Stats**: Monitor CPU, RAM, and Battery levels.
- **Clipboard Manager**: Read from and write to your clipboard.
- **Process Manager**: List running processes.

### 🖐️ Phase 2: The Hands
- **GUI Automation**: Move mouse, click, type text, and press hotkeys.
- **Screenshots**: Take instant screenshots of your desktop.
- **Window Management**: List and focus open windows.

### 🌐 Phase 3: The Browser
- **Web Automation**: Navigate websites and extract content using a headless browser (Playwright).
- **Web Screenshots**: Capture full-page screenshots of any URL.

### 📚 Phase 4: The Brain (Local RAG)
- **Chat with Notes**: Index your local `.md` and `.txt` files and ask Claude questions about them.
- **Semantic Search**: Uses FAISS and local embeddings for privacy.

### 🗣️ Phase 5: The Personality
- **Voice (TTS)**: Claude can speak to you using system Text-to-Speech.
- **Notifications**: Send system toast notifications.

### 👁️ Phase 6: The Eye & DJ
- **Webcam**: Take photos using your webcam.
- **Spotify Control**: Search and play songs on Spotify.
- **Media Control**: Play/Pause, Next/Prev, Volume control.

## 🚀 Installation

### Prerequisites
- Windows 10/11
- [Claude Desktop App](https://claude.ai/download)
- [uv](https://github.com/astral-sh/uv) (Fast Python package manager)
- `ffmpeg` (Optional, for future audio features)

### Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/exquisique/claude-jarvis.git
    cd claude-jarvis
    ```

2.  **Install Dependencies:**
    ```bash
    uv sync
    ```

3.  **Install into Claude Desktop:**
    Run this command to register the server with Claude:
    ```bash
    uv run fastmcp install claude-desktop main.py --with pywinauto --with psutil --with pyperclip --with pyautogui --with pillow --with playwright --with langchain --with langchain-community --with faiss-cpu --with sentence-transformers --with pyttsx3 --with plyer --with opencv-python
    ```

4.  **Restart Claude Desktop.**

## 🛠️ Usage

Once installed, simply open Claude Desktop and look for the 🔌 icon. You can now ask Claude to perform tasks like:

- "Take a screenshot and tell me what you see."
- "Open Spotify and play 'Bohemian Rhapsody'."
- "Check my CPU usage."
- "Index my notes in `C:/Documents/Notes` and tell me what I wrote about 'Project X'."
- "Take a selfie with the webcam."

## ⚠️ Troubleshooting

- **Timeout Errors**: If the server fails to start, it might be downloading large AI models. Run `uv sync` manually to pre-cache dependencies.
- **Admin Privileges**: Some features (like controlling certain apps) might require running Claude Desktop as Administrator.

## 📜 License

MIT
