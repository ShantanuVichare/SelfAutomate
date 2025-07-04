import time

from pynput import keyboard
import pyperclip

import logger

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
