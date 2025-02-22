
import subprocess
import platform

import base64
from io import BytesIO
import mss
from PIL import Image

import logger

def grab_screenshot():
    with mss.mss() as sct:
        sct_img = sct.grab(sct.monitors[1])
        return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
    

def image_pil_to_base64(image_pil):
    buffered = BytesIO()
    image_pil.save(buffered, format="PNG")
    image_data = buffered.getvalue()
    return base64.b64encode(image_data).decode("utf-8")

def copy_image_to_clipboard(file_path):
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.run(['osascript', '-e', f'set the clipboard to (read (POSIX file "{file_path}") as JPEG picture)'])
        elif system == "Windows":
            raise NotImplementedError(f"Unsupported OS: {system}")
        elif system == "Linux":
            with open(file_path, "rb") as f:
                subprocess.run(['xclip', '-selection', 'clipboard', '-t', 'image/png', '-i'], stdin=f)
        else:
            raise NotImplementedError(f"Unsupported OS: {system}")
    except Exception as e:
        logger.log(f"Failed to copy file to clipboard: {e}")

