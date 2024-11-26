import time
import os
from queue import Queue
from threading import Lock

from pynput import keyboard
import pyperclip

from dotenv import load_dotenv

from utils import image_pil_to_base64
from ui import ScreenTextTaskApp

load_dotenv()
if (os.getenv("GROQ_API_KEY") is not None):
    SELECTED_BACKEND = "groq"
else:
    SELECTED_BACKEND = "ollama"

if SELECTED_BACKEND == "groq":
    from modelClients.groq import send_to_groq, COMMANDS
    send_to_model = send_to_groq
    SUPPORTED_COMMANDS = list(COMMANDS.keys())
elif SELECTED_BACKEND == "ollama":
    from modelClients.ollama import send_to_ollama, COMMANDS
    send_to_model = send_to_ollama
    SUPPORTED_COMMANDS = list(COMMANDS.keys())
else:
    raise ValueError("Invalid backend selected with `SELECTED_BACKEND`. Please check supported backends.")


def run_model_command(cmd_idx, image):
    command_key = SUPPORTED_COMMANDS[cmd_idx]
    encoded_image = image_pil_to_base64(image)
    
    # Choice of model backend
    response = send_to_model(encoded_image, command_key)
    
    # Copy the response to the clipboard
    pyperclip.copy(response)

    
def main():
    # test_executability()
    
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
    
    while True:
        if not q.empty():
            if q.get() == "start":
                with signal_lock:
                    app = ScreenTextTaskApp(SUPPORTED_COMMANDS, run_model_command)
                    app.mainloop()
            else:
                break
        else:
            time.sleep(0.1)
    hotkeyListener.stop()
    

if __name__ == "__main__":
    main()
