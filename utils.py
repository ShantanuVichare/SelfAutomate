
import os
from datetime import datetime

import base64
from io import BytesIO

def image_pil_to_base64(image_pil):
    buffered = BytesIO()
    image_pil.save(buffered, format="PNG")
    image_data = buffered.getvalue()
    return base64.b64encode(image_data).decode("utf-8")


def test_executability():
    # Write current time to a file called "test" in user home
    home_directory = os.path.expanduser("~")
    file_path = os.path.join(home_directory, "text_detect_test.log")
    with open(file_path, "a") as file:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(current_time+"\n")