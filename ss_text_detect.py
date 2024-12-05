import time
import os
from queue import Queue
from threading import Lock
from multiprocessing import Process

from pynput import keyboard
import pyperclip

from dotenv import load_dotenv

from pushbullet import PushbulletWrapper, handle_push
from utils import test_executability, image_pil_to_base64
from ui import ScreenTextTaskApp

load_dotenv()
if (os.getenv("GROQ_API_KEY") is not None):
    SELECTED_BACKEND = "groq"
else:
    SELECTED_BACKEND = "ollama"

# SELECTED_BACKEND = "MOCK"

if SELECTED_BACKEND == "groq":
    from modelClients.groq import send_to_groq, COMMANDS
    send_to_model = send_to_groq
    SUPPORTED_COMMANDS = list(COMMANDS.keys())
elif SELECTED_BACKEND == "ollama":
    from modelClients.ollama import send_to_ollama, COMMANDS
    send_to_model = send_to_ollama
    SUPPORTED_COMMANDS = list(COMMANDS.keys())
elif SELECTED_BACKEND == "MOCK":
    send_to_model = lambda x, y: "MOCK_RESPONSE"
    SUPPORTED_COMMANDS = ["MOCK_COMMAND"]
else:
    raise ValueError("Invalid backend selected with `SELECTED_BACKEND`. Please check supported backends.")


def run_model_command(cmd_idx, image):
    command_key = SUPPORTED_COMMANDS[cmd_idx]
    encoded_image = image_pil_to_base64(image)
    
    # Choice of model backend
    response = send_to_model(encoded_image, command_key)
    
    # Copy the response to the clipboard
    pyperclip.copy(response)

def run_pushbullet_in_background():
    pb_config_path = os.getenv("PUSHBULLET_CONFIG_PATH")
    if pb_config_path is None:
        raise ValueError("PUSHBULLET_CONFIG_PATH not set in environment variables.")
    return PushbulletWrapper(config_path=pb_config_path).listen_push_notifications(handle_push)

def run_ui():
    app = ScreenTextTaskApp(SUPPORTED_COMMANDS, run_model_command)
    app.mainloop()
    
def main():
    # Useful for Debugging environment changes
    # test_executability()
    # exit()
    
    # Start the Pushbullet listener in the background
    pb_thread = run_pushbullet_in_background()
    
    # Start the Hotkey listener with message passing
    signal_lock = Lock()
    q = Queue()
    def start_ui_signal():
        if signal_lock.acquire(blocking=False):
            q.put("start")
            signal_lock.release()
    def end_ui_signal():
        if signal_lock.acquire(blocking=False):
            q.put("end")
            signal_lock.release()
    keyboard_mapping = {
        '<cmd>+<shift>+9': start_ui_signal,
        '<cmd>+<shift>+0': end_ui_signal,
    }
    hotkeyListener = keyboard.GlobalHotKeys(keyboard_mapping)
    hotkeyListener.start()
    
    # Wait for the signal to trigger UI launch
    while True:
        if not q.empty():
            if q.get() == "start":
                with signal_lock:
                    p = Process(target=run_ui)
                    p.start()
                    p.join()
            else:
                break
        else:
            time.sleep(0.2)
    
    # Cleanup tasks
    pb_thread.stop()
    hotkeyListener.stop()
    

if __name__ == "__main__":
    main()
