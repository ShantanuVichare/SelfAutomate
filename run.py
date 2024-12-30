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
        pb.listen(handle_push, 60)
    else:
        print("Warning: PUSHBULLET_CONFIG_PATH not set in environment variables. Skipping Pushbullet startup!")

def run_ui():
    app = ScreenTextTaskApp(SUPPORTED_COMMANDS, run_model_command)
    app.mainloop()
    
    
def CreateProcess(name):
    match name:
        case "pb":
            return Process(target=run_pushbullet, name=name)
        case "ui":
            return Process(target=run_ui, name=name)
        case _:
            raise ValueError(f"Unknown process identifier name: {name}")
        
def ResetProcess(proc):
    if proc.is_alive():
        proc.terminate()
    if proc.pid:
        proc = CreateProcess(proc.name)
    return proc
    
def main():
    # Useful for Debugging environment changes
    # logger.test_executability()
    # exit()
    
    logger.mark_process_run()
    logger.log("Starting SelfAutomate")
    
    # Init processes
    pb_process = CreateProcess("pb")
    ui_process = CreateProcess("ui")
    
    
    # Start the Hotkey listener with message passing
    q = Queue()
    def start_pb_signal():
        q.put("start_pb")
    def start_ui_signal():
        q.put("start_ui")
    def end_signal():
        q.put("end")
    hotkeyListener = keyboard.GlobalHotKeys({
        '<cmd>+<shift>+8': start_pb_signal,
        '<cmd>+<shift>+9': start_ui_signal,
        '<cmd>+<shift>+0': end_signal,
    })
    hotkeyListener.start()
    
    
    # Background processes
    # pb_process.start()
    
    try:
        # Wait for the signal to trigger UI launch
        while True:
            if not q.empty():
                signal = q.get()
                logger.log(f"Received signal: {signal}")
                if signal == "start_ui":
                    ui_process = ResetProcess(ui_process)
                    ui_process.start()
                elif signal == "start_pb":
                    pb_process = ResetProcess(pb_process)
                    pb_process.start()
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
