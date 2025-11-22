from fastmcp import FastMCP
from pywinauto import Desktop, Application
import re

# Initialize the MCP server
mcp = FastMCP("desktop-automation")

@mcp.tool()
def list_windows() -> list[str]:
    """
    Lists the titles of all currently visible windows on the desktop.
    Returns a list of strings, where each string is a window title.
    """
    try:
        # 'uia' backend is better for modern applications (Chrome, VS Code, etc.)
        desktop = Desktop(backend="uia")
        windows = desktop.windows()
        
        # Filter out windows with empty titles and return the list
        window_titles = [w.window_text() for w in windows if w.window_text()]
        return list(set(window_titles)) # Remove duplicates
    except Exception as e:
        return [f"Error listing windows: {str(e)}"]

@mcp.tool()
def focus_window(title_substring: str) -> str:
    """
    Brings a window to the foreground (focuses it) based on a substring of its title.
    
    Args:
        title_substring: A part of the window title to search for (case-insensitive).
    """
    try:
        desktop = Desktop(backend="uia")
        # Find windows that match the substring
        windows = desktop.windows()
        matches = [w for w in windows if title_substring.lower() in w.window_text().lower()]
        
        if not matches:
            return f"No window found containing '{title_substring}'"
        
        # Pick the first match (or maybe the one with the shortest title? logic can be improved)
        target_window = matches[0]
        actual_title = target_window.window_text()
        
        # Restore if minimized, then focus
        if target_window.get_show_state() == 2: # 2 is Minimized
            target_window.restore()
            
        target_window.set_focus()
        return f"Successfully focused: '{actual_title}'"
        
    except Exception as e:
        return f"Failed to focus window matching '{title_substring}': {str(e)}"

@mcp.tool()
def open_application(app_name: str) -> str:
    """
    Opens an application by name.
    
    Args:
        app_name: The name of the application to open (e.g., 'notepad', 'calc', 'spotify', 'chrome').
                  This works best with applications that are in the system PATH or registered in Windows.
    """
    import subprocess
    try:
        # Use 'start' command in Windows shell to launch the app
        # This leverages Windows' own ability to find apps by name
        subprocess.Popen(f"start {app_name}", shell=True)
        return f"Attempted to open '{app_name}'"
    except Exception as e:
        return f"Failed to open '{app_name}': {str(e)}"

@mcp.tool()
def media_control(action: str) -> str:
    """
    Controls media playback.
    
    Args:
        action: One of 'play_pause', 'next', 'prev', 'stop'.
    """
    from pywinauto.keyboard import send_keys
    
    try:
        if action == 'play_pause':
            send_keys('{MEDIA_PLAY_PAUSE}')
        elif action == 'next':
            send_keys('{MEDIA_NEXT_TRACK}')
        elif action == 'prev':
            send_keys('{MEDIA_PREV_TRACK}')
        elif action == 'stop':
            send_keys('{MEDIA_STOP}')
        else:
            return f"Unknown media action: {action}"
        return f"Executed media action: {action}"
    except Exception as e:
        return f"Failed to execute media action '{action}': {str(e)}"

@mcp.tool()
def volume_control(action: str, steps: int = 5) -> str:
    """
    Controls system volume.
    
    Args:
        action: One of 'up', 'down', 'mute'.
        steps: Number of steps to increase/decrease volume (default 5). Ignored for 'mute'.
    """
    from pywinauto.keyboard import send_keys
    
    try:
        if action == 'mute':
            send_keys('{VOLUME_MUTE}')
            return "Toggled mute"
        
        key = '{VOLUME_UP}' if action == 'up' else '{VOLUME_DOWN}' if action == 'down' else None
        
        if not key:
            return f"Unknown volume action: {action}"
            
        # Press the key 'steps' times
        for _ in range(steps):
            send_keys(key)
            
        return f"Volume {action} by {steps} steps"
    except Exception as e:
        return f"Failed to execute volume action '{action}': {str(e)}"

# --- Phase 1: System Context Tools ---

@mcp.tool()
def get_system_stats() -> str:
    """
    Returns current system statistics: CPU usage, RAM usage, and Battery status.
    """
    import psutil
    
    cpu = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    battery = psutil.sensors_battery()
    
    battery_status = "Unknown"
    if battery:
        battery_status = f"{battery.percent}% ({'Plugged in' if battery.power_plugged else 'On Battery'})"
        
    return (
        f"CPU Usage: {cpu}%\n"
        f"RAM Usage: {memory.percent}% ({memory.used / (1024**3):.2f}GB / {memory.total / (1024**3):.2f}GB)\n"
        f"Battery: {battery_status}"
    )

@mcp.tool()
def list_processes(limit: int = 10) -> str:
    """
    Lists the top running processes by memory usage.
    
    Args:
        limit: Number of processes to list (default 10).
    """
    import psutil
    
    procs = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
        try:
            procs.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            
    # Sort by memory usage
    procs.sort(key=lambda p: p['memory_percent'] or 0, reverse=True)
    
    output = "Top Processes by Memory:\n"
    for p in procs[:limit]:
        mem = p['memory_percent'] or 0
        output += f"- {p['name']} (PID: {p['pid']}): {mem:.1f}%\n"
        
    return output

@mcp.tool()
def clipboard_read() -> str:
    """
    Reads the current content of the system clipboard.
    """
    import pyperclip
    try:
        content = pyperclip.paste()
        return f"Clipboard Content:\n{content}"
    except Exception as e:
        return f"Failed to read clipboard: {str(e)}"

@mcp.tool()
def clipboard_write(content: str) -> str:
    """
    Writes text to the system clipboard.
    
    Args:
        content: The text to copy to the clipboard.
    """
    import pyperclip
    try:
        pyperclip.copy(content)
        return "Successfully copied to clipboard."
    except Exception as e:
        return f"Failed to write to clipboard: {str(e)}"

# --- Phase 2: GUI Automation Tools ---

@mcp.tool()
def take_screenshot() -> str:
    """
    Takes a screenshot of the primary screen and returns it as a base64 encoded string.
    """
    import pyautogui
    import base64
    from io import BytesIO
    
    try:
        # Capture screenshot
        screenshot = pyautogui.screenshot()
        
        # Convert to base64
        buffered = BytesIO()
        screenshot.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        return f"Screenshot taken. Base64 length: {len(img_str)}. Data: data:image/png;base64,{img_str}"
    except Exception as e:
        return f"Failed to take screenshot: {str(e)}"

@mcp.tool()
def click_at(x: int, y: int) -> str:
    """
    Moves the mouse to (x, y) and clicks.
    """
    import pyautogui
    try:
        pyautogui.click(x, y)
        return f"Clicked at ({x}, {y})"
    except Exception as e:
        return f"Failed to click at ({x}, {y}): {str(e)}"

@mcp.tool()
def type_text(text: str, interval: float = 0.0) -> str:
    """
    Types the given text.
    
    Args:
        text: The string to type.
        interval: Delay between each character (default 0.0).
    """
    import pyautogui
    try:
        pyautogui.write(text, interval=interval)
        return f"Typed text: '{text}'"
    except Exception as e:
        return f"Failed to type text: {str(e)}"

@mcp.tool()
def press_hotkey(keys: str) -> str:
    """
    Presses a hotkey combination.
    
    Args:
        keys: A string of keys separated by '+', e.g., 'ctrl+c', 'alt+tab', 'win+r'.
    """
    import pyautogui
    try:
        key_list = keys.split('+')
        # Clean up whitespace
        key_list = [k.strip().lower() for k in key_list]
        pyautogui.hotkey(*key_list)
        return f"Pressed hotkey: {keys}"
    except Exception as e:
        return f"Failed to press hotkey '{keys}': {str(e)}"

@mcp.tool()
def get_screen_size() -> str:
    """
    Returns the width and height of the screen.
    """
    import pyautogui
    width, height = pyautogui.size()
    return f"Screen Size: {width}x{height}"



# --- Phase 2.5: Browser Automation Tools ---

@mcp.tool()
def browser_navigate(url: str) -> str:
    """
    Navigates to a URL using a headless browser and returns the page title and text content.
    """
    from playwright.sync_api import sync_playwright
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            title = page.title()
            content = page.inner_text('body')
            browser.close()
            
            # Truncate content to avoid hitting token limits
            return f"Page Title: {title}\n\nContent Snippet:\n{content[:500]}..."
    except Exception as e:
        return f"Failed to navigate to {url}: {str(e)}"

@mcp.tool()
def browser_screenshot(url: str) -> str:
    """
    Navigates to a URL and takes a screenshot. Returns base64 image.
    """
    from playwright.sync_api import sync_playwright
    import base64
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            screenshot_bytes = page.screenshot()
            browser.close()
            
            img_str = base64.b64encode(screenshot_bytes).decode("utf-8")
            return f"Screenshot of {url} taken. Data: data:image/png;base64,{img_str}"
    except Exception as e:
        return f"Failed to take browser screenshot: {str(e)}"



# --- Phase 3: Local RAG Tools ---

# Global variable to hold the vector store in memory for simplicity
# In a real app, you'd persist this to disk
vector_store = None

@mcp.tool()
def index_notes(directory_path: str) -> str:
    """
    Indexes text files (.txt, .md) in the given directory for semantic search.
    This might take a while for many files.
    """
    global vector_store
    import os
    from langchain_community.document_loaders import DirectoryLoader, TextLoader
    from langchain_community.vectorstores import FAISS
    from langchain_community.embeddings import HuggingFaceEmbeddings
    
    try:
        if not os.path.exists(directory_path):
            return f"Directory not found: {directory_path}"
            
        # Load documents
        loader = DirectoryLoader(directory_path, glob="**/*.md", loader_cls=TextLoader)
        docs = loader.load()
        
        if not docs:
             # Try .txt if no .md found
            loader = DirectoryLoader(directory_path, glob="**/*.txt", loader_cls=TextLoader)
            docs = loader.load()
            
        if not docs:
            return "No .md or .txt files found to index."
            
        # Create embeddings and vector store
        # Using a small, fast model
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vector_store = FAISS.from_documents(docs, embeddings)
        
        return f"Successfully indexed {len(docs)} documents from {directory_path}."
        
    except Exception as e:
        return f"Failed to index notes: {str(e)}"

@mcp.tool()
def query_notes(query: str) -> str:
    """
    Searches the indexed notes for the given query and returns relevant snippets.
    You must call index_notes() first.
    """
    global vector_store
    
    if vector_store is None:
        return "No notes indexed yet. Please call index_notes(directory_path) first."
        
    try:
        # Search
        results = vector_store.similarity_search(query, k=3)
        
        output = f"Results for '{query}':\n\n"
        for doc in results:
            source = doc.metadata.get('source', 'Unknown')
            content = doc.page_content[:500].replace('\n', ' ') # Truncate and clean
            output += f"--- Source: {source} ---\n{content}...\n\n"
            
        return output
    except Exception as e:
        return f"Failed to query notes: {str(e)}"



# --- Phase 4: The Personality Tools ---

@mcp.tool()
def speak_text(text: str) -> str:
    """
    Speaks the given text using the system's text-to-speech engine.
    """
    import pyttsx3
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        return f"Spoke: '{text}'"
    except Exception as e:
        return f"Failed to speak text: {str(e)}"

@mcp.tool()
def show_notification(title: str, message: str) -> str:
    """
    Shows a system notification (toast).
    """
    from plyer import notification
    try:
        notification.notify(
            title=title,
            message=message,
            app_name='Claude Automation',
            timeout=10
        )
        return f"Notification sent: {title} - {message}"
    except Exception as e:
        return f"Failed to show notification: {str(e)}"



# --- Phase 5 & 6: The Eye & DJ Pro ---

@mcp.tool()
def take_webcam_photo() -> str:
    """
    Captures a photo from the default webcam and returns it as a base64 string.
    """
    import cv2
    import base64
    
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return "Failed to open webcam."
            
        # Warm up camera
        for _ in range(5):
            cap.read()
            
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return "Failed to capture frame."
            
        # Encode to JPG
        _, buffer = cv2.imencode('.jpg', frame)
        img_str = base64.b64encode(buffer).decode("utf-8")
        
        return f"Webcam photo taken. Data: data:image/jpeg;base64,{img_str}"
    except Exception as e:
        return f"Failed to take webcam photo: {str(e)}"

@mcp.tool()
def play_specific_song(song_name: str) -> str:
    """
    Plays a specific song on Spotify.
    WARNING: This assumes Spotify is installed and logged in.
    It opens Spotify search and simulates pressing 'Enter' to play the top result.
    """
    import subprocess
    import pyautogui
    import time
    
    try:
        # Open Spotify to the search page for the song
        # The URI scheme 'spotify:search:query' opens the search tab
        query = song_name.replace(" ", "%20")
        subprocess.Popen(f"start spotify:search:{query}", shell=True)
        
        # Wait for Spotify to open and load (adjust time if needed)
        time.sleep(3.0) 
        
        # Press 'Enter' to select the top result (usually the song)
        # Sometimes you need to tab down, but usually 'Enter' on the search result plays it
        # Let's try a sequence: Tab -> Enter (to be safe, or just Enter)
        # Actually, on modern Spotify, 'spotify:search:xyz' just shows results. 
        # You often need to click the "Play" button next to the top result.
        # Let's try a generic "Play" macro: Tab, Tab, Enter? 
        # Or just tell the user "I opened it, you click play".
        # BUT the user asked "it plays".
        # Let's try: Tab -> Enter.
        
        pyautogui.press('tab')
        time.sleep(0.5)
        pyautogui.press('enter')
        
        return f"Opened Spotify for '{song_name}' and attempted to play."
    except Exception as e:
        return f"Failed to play song: {str(e)}"

if __name__ == "__main__":
    mcp.run()
