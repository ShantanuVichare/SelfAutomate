from datetime import datetime
import os
import json
from traceback import print_exception

# Variables for logging
PID = str(os.getpid())

LOG_DIR = os.getenv("LOG_DIR")
if LOG_DIR is None:
    LOG_DIR = os.path.join(os.path.expanduser("~"), ".self_dev")
    os.makedirs(LOG_DIR, exist_ok=True)
    print(f"LOG_DIR not set in environment variables. Defaulting to {LOG_DIR}")
    os.environ["LOG_DIR"] = LOG_DIR

RUNNING_FILE = "running_lock.json"
EXECUTABILITY_FILE = "text_detect_test.log"
PROCESS_LOG_FILE = "process.log"

def getCurrentTime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def check_pid_exists(pid_num: int) -> bool:
    """
    Checks if a process with the given PID exists.

    Args:
        pid_num (int): The process ID to check.

    Returns:
        bool: True if the process exists, False otherwise.
    """
    try:
        os.kill(pid_num, 0)  # Send signal 0, which does not kill the process
        return True
    except ValueError:
        # PID is not a valid integer
        return False
    except ProcessLookupError:
        return False
    except PermissionError:
        # Operation not permitted, but process exists
        return True
    except OSError:
        return False

def allow_running_instance(time_delta: int = None) -> bool:
    current_time = datetime.now().timestamp()
    run_config = access_runtime_config(RUNNING_FILE)
    # Store PID and last check time
    last_check_time = run_config.get("last_check_time", None)
    last_pid = run_config.get("last_pid", None)
    if last_pid is None or last_check_time is None:
        run_config["last_pid"] = PID
        run_config["last_check_time"] = current_time
        access_runtime_config(RUNNING_FILE, run_config)
        return True
    
    last_check_time = float(last_check_time)
    
    if last_pid == PID:
        run_config["last_check_time"] = current_time
        access_runtime_config(RUNNING_FILE, run_config)
        return True
    
    last_pid_num = int(last_pid)
    
    if time_delta is not None:
        if current_time - last_check_time < time_delta:
            return False
        while check_pid_exists(last_pid_num):
            import time
            import signal
            # Terminate previous process
            os.kill(last_pid_num, signal.SIGTERM)
            # Sleep - to allow process to terminate
            time.sleep(1)
        # Update with current process
        run_config["last_pid"] = PID
        run_config["last_check_time"] = current_time
        access_runtime_config(RUNNING_FILE, run_config)
        return True
    return False
    
def terminate_running_instance():
    access_runtime_config(RUNNING_FILE, {})
        
###########

def test_executability():
    file_path = os.path.join(LOG_DIR, EXECUTABILITY_FILE)
    with open(file_path, "a") as file:
        file.write(f"PID: {PID}\n")
        current_time = getCurrentTime()
        file.write(f"Current time: {current_time}\n")
        current_dir = os.getcwd()
        file.write(f"Current directory: {current_dir}\n")
        
def log(*args):
    file_path = os.path.join(LOG_DIR, PROCESS_LOG_FILE)
    current_time = getCurrentTime()
    with open(file_path, "a") as file:
        print(f"[{PID}][{current_time}]:", *args, file=file)

def log_debug(*args):
    file_path = os.path.join(LOG_DIR, PROCESS_LOG_FILE)
    current_time = getCurrentTime()
    with open(file_path, "a") as file:
        print(f"[{PID}][{current_time}]: [DEBUG] -", *args, file=file)

def log_error(exception: Exception, *args):
    file_path = os.path.join(LOG_DIR, PROCESS_LOG_FILE)
    current_time = getCurrentTime()
    with open(file_path, "a") as file:
        print(f"[{PID}][{current_time}]: [ERROR] -", *args, file=file)
        print_exception(exception, file=file)

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
