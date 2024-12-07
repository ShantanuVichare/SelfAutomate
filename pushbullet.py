import time
from datetime import datetime
import json
import os
import threading
import platform
import requests
import tempfile
import shutil
import webbrowser
import pyperclip  # Ensure you have this library installed

from typing import Callable

from utils import copy_image_to_clipboard, log

# Docs: https://docs.pushbullet.com/

class PushbulletWrapper:
    def __init__(self, config_path='pushbullet_config.json'):
        self.config_path = config_path
        self.api_key = None
        self.device = None
        self.load_config()

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                self.api_key = config.get('api_key')
                self.device = config.get('device')
        if not self.api_key:
            self.api_key = input("Enter your Pushbullet API key: ")
        if not self.device:
            self.device = self.create_device()
        self.save_config()

    def save_config(self):
        with open(self.config_path, 'w') as f:
            json.dump({'api_key': self.api_key, 'device': self.device}, f)

    def create_device(self):
        headers = {'Access-Token': self.api_key, 'Content-Type': 'application/json'}
        device_data = {
            "nickname": platform.node() + "-" + datetime.now().strftime("%m%d%y"),
            # "type": "stream",
            "model": "SelfAutomate",
            "manufacturer": "Shantanu"
        }
        response = requests.post('https://api.pushbullet.com/v2/devices', headers=headers, data=json.dumps(device_data))
        response.raise_for_status()
        return response.json()

    def get_devices(self):
        headers = {'Access-Token': self.api_key}
        response = requests.get('https://api.pushbullet.com/v2/devices', headers=headers)
        response.raise_for_status()
        return response.json().get('devices', [])
    
    def listen(self, callback: Callable):
        headers = {'Access-Token': self.api_key}
        url = 'https://api.pushbullet.com/v2/pushes'
        last_timestamp = time.time()
        while True:
            params = {'modified_after': last_timestamp, 'active': 'true', 'limit': 10}
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                pushes = response.json().get('pushes', [])
                for push in reversed(pushes):
                    if push.get('target_device_iden') == self.device['iden']:
                        callback(push)
                        last_timestamp = push.get('modified')
            time.sleep(2)  # Polling
        return None

def handle_push(push):
    push_type = push.get('type')
    if push_type == 'note':
        body = push.get('body', '')
        pyperclip.copy(body)
        log(f"Note copied to clipboard: {body}")
    elif push_type == 'link':
        url = push.get('url', '')
        webbrowser.open(url)
        log(f"Link opened in browser: {url}")
    elif push_type == 'file':
        file_url = push.get('file_url', '')
        response = requests.get(file_url, stream=True)
        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(delete=False, prefix='SelfAutomate.app_pushbullet_') as tmp_file:
                shutil.copyfileobj(response.raw, tmp_file)
                tmp_file_path = tmp_file.name
            
            if push.get('file_type', '').startswith('image/'):
                # Copy the image to clipboard
                copy_image_to_clipboard(tmp_file_path)
                log(f"Image copied to clipboard!")
            else:
                # Copy the file to downloads folder
                file_name = push.get('file_name', 'downloaded_file')
                downloads_path = os.path.join(os.path.expanduser('~/Downloads'), file_name)
                shutil.copy(tmp_file_path, downloads_path)
                log(f"File downloaded: {downloads_path}")
            os.remove(tmp_file_path)
        else:
            log(f"Failed to get image: {file_url}")

# pb = PushbulletWrapper()
# pb_thread = pb.listen_push_notifications(handle_push)
# pb_thread.join()

