import time
import os
from queue import Queue

from pynput import keyboard
import pyperclip

from dotenv import load_dotenv
load_dotenv()

from pushbullet import PushbulletWrapper, handle_push
import logger
from ui import ScreenTextTaskApp, GenericTaskApp, ForceStartDialog

from ProcessManager import ProcessManager


class ProcessType():
    pushbullet = "pushbullet"
    screentext_ui = "screentext_ui"
    clip_to_type = "clip_to_type"

def run_pushbullet():
    pb_config_path = os.getenv("PUSHBULLET_CONFIG_PATH")
    if pb_config_path is not None:
        pb = PushbulletWrapper(config_path=pb_config_path)
        pb.listen(handle_push, 60)
    else:
        print("Warning: PUSHBULLET_CONFIG_PATH not set in environment variables. Skipping Pushbullet startup!")

def run_screentext_task_ui():
    app = ScreenTextTaskApp()
    app.mainloop()
    

def run_clip_to_type():
    # Retrieve text from clipboard and simulate typing with human-like delay.
    text = pyperclip.paste()
    logger.log(f"Typing clipboard text. Length: {len(text)} chars")
    kb = keyboard.Controller()
    for char in text:
        if char == '\r' or char == '\x00' or char == '\x0b' or char == '\x0c':
            # Ignored characters: 
            #   \r (carriage return),
            #   \x00 (null character),
            #   \x0b (vertical tab),
            #   \x0c (form feed),
            continue
        elif char == '\n':
            kb.press(keyboard.Key.enter)
            kb.release(keyboard.Key.enter)
        elif char == '\t':
            kb.press(keyboard.Key.tab)
            kb.release(keyboard.Key.tab)
        elif char == ' ':
            kb.press(keyboard.Key.space)
            kb.release(keyboard.Key.space)
        else:
            # For other characters, just type them directly
            kb.press(char)
            kb.release(char)
        time.sleep(0.1)

PROCESS_MAP = {
    ProcessType.pushbullet: run_pushbullet,
    ProcessType.screentext_ui: run_screentext_task_ui,
    ProcessType.clip_to_type: run_clip_to_type,
}


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
        logger.log("SelfAutomate is already running. Not starting a new instance.")
        exit()
    logger.log("Starting SelfAutomate")
    
    pm = ProcessManager(PROCESS_MAP)

    # Start the Hotkey listener with message passing
    q = Queue()
    def start_pb_signal():
        q.put(ProcessType.pushbullet)
    def start_ui_signal():
        q.put(ProcessType.screentext_ui)
    def type_clipboard_signal():
        q.put(ProcessType.clip_to_type)
    def end_signal():
        q.put("end")
    
    try:
        # Register hotkeys
        hotkeyListener = keyboard.GlobalHotKeys({
            '<cmd>+<shift>+7': type_clipboard_signal,
            '<cmd>+<shift>+8': start_pb_signal,
            '<cmd>+<shift>+9': start_ui_signal,
            '<cmd>+<shift>+0': end_signal,
        })
        hotkeyListener.start()
        
        # Background processes
        # None for now - Use pm.create_process

        # Signal loop
        loop_delayer = 5
        # Wait for the signal to trigger UI launch
        while True:
            if not q.empty():
                signal = q.get()
                logger.log(f"Received signal: {signal}")
                if signal == ProcessType.screentext_ui:
                    pm.reset_process(ProcessType.screentext_ui)
                elif signal == ProcessType.pushbullet:
                    pm.reset_process(ProcessType.pushbullet)
                elif signal == ProcessType.clip_to_type:
                    pm.reset_process(ProcessType.clip_to_type, force_restart=False)
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
        pm.terminate_all()
        hotkeyListener.stop()
        logger.terminate_running_instance()
        logger.log("Termination successful!\n")
    

if __name__ == "__main__":
    main()
