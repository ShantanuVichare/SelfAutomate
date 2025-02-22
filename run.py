import time
import os
from queue import Queue
from threading import Lock
from multiprocessing import Process

from pynput import keyboard
import pyperclip

from dotenv import load_dotenv
load_dotenv()

from pushbullet import PushbulletWrapper, handle_push
from utils import image_pil_to_base64
import logger
from ui import ScreenTextTaskApp, ForceStartDialog

from modelClients.main import Command, COMMANDS



def run_model_command(command: Command, image):
    encoded_image = image_pil_to_base64(image)
    
    # Choice of model backend
    response = command.execute(encoded_image=encoded_image)
    
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
    app = ScreenTextTaskApp(COMMANDS, run_model_command)
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
    
    if not logger.allow_running_instance(2):
        
        # user_confirmed = ForceStartDialog().confirm()
        # if user_confirmed:
        #     logger.log("Force starting SelfAutomate")
        #     logger.mark_process_end()
        #     logger.mark_process_run()
        # else:
        #     logger.log("Exiting as per user request")
        #     exit()
        logger.log("SelfAutomate is already running. Exiting...")
        exit()
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
    # 
    
    try:
        loop_delayer = 5
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
            loop_delayer -= 1
            if loop_delayer == 0:
                loop_delayer = 5
                if not logger.allow_running_instance():
                    logger.log("SelfAutomate delayed termination")
                    break
    finally:
        logger.log("Terminating SelfAutomate")
        if pb_process and pb_process.is_alive(): pb_process.terminate()
        if ui_process and ui_process.is_alive(): ui_process.terminate()
        hotkeyListener.stop()
        logger.terminate_running_instance()
        logger.log("Termination successful!")
    

if __name__ == "__main__":
    main()
