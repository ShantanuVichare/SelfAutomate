
from datetime import datetime
import os
import subprocess
import platform

import base64
from io import BytesIO

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
        print(f"Failed to copy file to clipboard: {e}")

def test_executability():
    # Write current time to a file called "test" in user home
    home_directory = os.path.expanduser("~")
    file_path = os.path.join(home_directory, "text_detect_test.log")
    with open(file_path, "a") as file:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"Current time: {current_time}\n")
        current_dir = os.getcwd()
        file.write(f"Current directory: {current_dir}\n")