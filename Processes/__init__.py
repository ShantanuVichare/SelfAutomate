
from multiprocessing import Process

import logger

from Processes.pushbullet import run_pushbullet
from Processes.ui import run_screentext_task_ui
from Processes.clipboardType import run_clip_to_type


class ProcessType():
    def __init__(self, key, hotkey, force_restart=True):
        self.key = key
        self.hotkey = hotkey
        self.force_restart = force_restart

    def run(self, *args, **kwargs):
        raise NotImplementedError("Subclasses should implement this method.")

class PTPushbullet(ProcessType):
    def __init__(self):
        super().__init__("pushbullet", '<cmd>+<shift>+8')

    def run(self, *args, **kwargs):
        return run_pushbullet(*args, **kwargs)

class PTScreentextUI(ProcessType):
    def __init__(self):
        super().__init__("screentext_ui", '<cmd>+<shift>+9')

    def run(self, *args, **kwargs):
        return run_screentext_task_ui(*args, **kwargs)

class PTClipToType(ProcessType):
    def __init__(self):
        super().__init__("clip_to_type", '<cmd>+<shift>+7', force_restart=False)

    def run(self, *args, **kwargs):
        return run_clip_to_type(*args, **kwargs)


PROCESS_TYPE_MAP: dict[str, ProcessType] = {
    pt.key: pt for pt in [PTPushbullet(), PTScreentextUI(), PTClipToType()]
}

class ProcessManager:
    def __init__(self):
        self.process_type_map = PROCESS_TYPE_MAP
        self.running_processes = {}

    def create_process(self, name, process_args=()):
        if name not in self.process_type_map:
            raise ValueError(f"Unknown process identifier name: {name}")
        if name in self.running_processes:
            logger.log(f"Process {name} already exists")
            return
        logger.log(f"Creating new process: {name} with args: {process_args}")
        proc_runner = self.process_type_map[name]
        self.running_processes[name] = Process(target=proc_runner.run, args=process_args, name=name)

    def reset_process(self, name, process_args=()):
        if name not in self.process_type_map:
            raise ValueError(f"Unknown process identifier name: {name}")
        proc_runner = self.process_type_map[name]
        was_running = name in self.running_processes and self.running_processes[name].is_alive()
        self.terminate_process(name)
        if proc_runner.force_restart or not was_running:
            self.create_process(name, process_args)
            self.running_processes[name].start()
            logger.log(f"Started process: {name}")
    
    def terminate_process(self, name):
        if name not in self.running_processes:
            # IGNORED: Process not running
            return
        if self.running_processes[name].is_alive():
            logger.log(f"Terminating process: {name}")
            self.running_processes[name].terminate()
        del self.running_processes[name]
        return
    
    def terminate_all(self):
        logger.log("Terminating all processes")
        for name in list(self.running_processes.keys()):
            self.terminate_process(name)
        return

