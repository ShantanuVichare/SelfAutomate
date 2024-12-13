import time
import os
from queue import Queue
from threading import Lock
from multiprocessing import Process

from pynput import keyboard
import pyperclip

from dotenv import load_dotenv

from pushbullet import PushbulletWrapper, handle_push
from utils import image_pil_to_base64
import logger
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


def run_pushbullet():
    pb_config_path = os.getenv("PUSHBULLET_CONFIG_PATH")
    if pb_config_path is not None:
        pb = PushbulletWrapper(config_path=pb_config_path)
        pb.listen(handle_push)
    else:
        print("Warning: PUSHBULLET_CONFIG_PATH not set in environment variables. Skipping Pushbullet startup!")

def run_ui():
    app = ScreenTextTaskApp(SUPPORTED_COMMANDS, run_model_command)
    app.mainloop()
    
def main():
    # Useful for Debugging environment changes
    # logger.test_executability()
    # exit()
    
    logger.mark_process_run()
    
    # Init processes
    pb_process = Process(target=run_pushbullet)
    ui_process = Process(target=run_ui)
    
    
    # Start the Hotkey listener with message passing
    q = Queue()
    def start_ui_signal():
        q.put("start_ui")
    def end_ui_signal():
        q.put("end")
    hotkeyListener = keyboard.GlobalHotKeys({
        '<cmd>+<shift>+9': start_ui_signal,
        '<cmd>+<shift>+0': end_ui_signal,
    })
    hotkeyListener.start()
    
    
    # Background processes
    pb_process.start()
    
    try:
        # Wait for the signal to trigger UI launch
        while True:
            if not q.empty():
                signal = q.get()
                logger.log(f"Received signal: {signal}")
                if signal == "start_ui":
                    if ui_process.is_alive():
                        ui_process.terminate()
                    if ui_process.pid:
                        ui_process = Process(target=run_ui)
                    ui_process.start()
                elif signal == "end":
                    break
                else:
                    continue
            else:
                time.sleep(0.2)
    finally:
        logger.log("Terminating SelfAutomate")
        if pb_process and pb_process.is_alive(): pb_process.terminate()
        if ui_process and ui_process.is_alive(): ui_process.terminate()
        hotkeyListener.stop()
        logger.mark_process_end()
        logger.log("Termination successful!")
    

if __name__ == "__main__":
    main()
