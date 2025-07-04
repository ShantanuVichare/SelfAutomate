import time
import os
from queue import Queue

from pynput.keyboard import GlobalHotKeys

from dotenv import load_dotenv
load_dotenv()

import logger

from Processes import ProcessManager, PROCESS_TYPE_MAP


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
    
    pm = ProcessManager()

    # Start the Hotkey listener with message passing
    q = Queue()
    def get_process_signal_listener(signal_key: str):
        def start_signal():
            q.put(signal_key)
        return start_signal
    
    hotkeyMap = {
        pt.hotkey: get_process_signal_listener(pt.key) for pt in PROCESS_TYPE_MAP.values()
    }
    hotkeyMap['<cmd>+<shift>+0'] = get_process_signal_listener("end_signal")
    
    try:
        # Register hotkeys
        hotkeyListener = GlobalHotKeys(hotkeyMap)
        hotkeyListener.start()

        # Background processes
        # None for now - Use pm.create_process

        # Signal loop
        loop_delayer = 5
        # Wait for the signal to trigger UI launch
        while True:
            if not q.empty():
                signal = q.get()
                logger.log(f"Received process signal: {signal}")
                if signal in PROCESS_TYPE_MAP:
                    pm.reset_process(signal)
                elif signal == "end_signal":
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
