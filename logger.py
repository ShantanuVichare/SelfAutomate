from datetime import datetime
import os
import json

# Variables for logging
PID = str(os.getpid())

LOG_DIR = os.getenv("LOG_DIR")
if LOG_DIR is None:
    LOG_DIR = os.path.join(os.path.expanduser("~"), ".self_dev")
    os.makedirs(LOG_DIR, exist_ok=True)
    print(f"LOG_DIR not set in environment variables. Defaulting to {LOG_DIR}")
    os.environ["LOG_DIR"] = LOG_DIR

RUNNING_FILE = "running_lock.log"
EXECUTABILITY_FILE = "text_detect_test.log"
PROCESS_LOG_FILE = "process.log"

def mark_process_run():
    file_path = os.path.join(LOG_DIR, RUNNING_FILE)
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            lines = f.readlines()
        pid = lines[0].split()[-1]
        raise Exception(f"SelfAutomate is already running. PID: {pid}")
    else:
        with open(file_path, "w") as f:
            f.write(f"Running SelfAutomate with PID: {os.getpid()}")

def mark_process_end():
    file_path = os.path.join(LOG_DIR, RUNNING_FILE)
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        raise Exception("No running instance found to end.")

def test_executability():
    file_path = os.path.join(LOG_DIR, EXECUTABILITY_FILE)
    with open(file_path, "a") as file:
        file.write(f"PID: {PID}\n")
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"Current time: {current_time}\n")
        current_dir = os.getcwd()
        file.write(f"Current directory: {current_dir}\n")
        
def log(*args):
    file_path = os.path.join(LOG_DIR, PROCESS_LOG_FILE)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(file_path, "a") as file:
        print(f"[{PID}][{current_time}]:", *args, file=file)

def access_runtime_config(config_file_path, config: dict = None) -> dict:
    file_path = os.path.join(LOG_DIR, config_file_path)
    if config is None:
        try:
            with open(file_path, "r") as file:
                config = json.load(file)
        except FileNotFoundError:
            config = {}
    else:
        with open(file_path, "w") as file:
            json.dump(config, file)
    return config
