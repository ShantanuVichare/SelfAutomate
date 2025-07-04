
from multiprocessing import Process

import logger

class ProcessManager:
    def __init__(self, process_map):
        self.process_map = process_map
        self.running_processes = {}

    def create_process(self, name, process_args=()):
        if name not in self.process_map:
            raise ValueError(f"Unknown process identifier name: {name}")
        if name in self.running_processes:
            logger.log(f"Process {name} already exists")
            return
        logger.log(f"Creating new process: {name} with args: {process_args}")
        self.running_processes[name] = Process(target=self.process_map[name], args=process_args, name=name)

    def reset_process(self, name, force_restart=True, process_args=()):
        if name not in self.process_map:
            raise ValueError(f"Unknown process identifier name: {name}")
        was_running = name in self.running_processes and self.running_processes[name].is_alive()
        self.terminate_process(name)
        if force_restart or not was_running:
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

