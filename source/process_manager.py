from config import load_config
from multiprocessing.pool import Pool
from multiprocessing import Process
from finder import start_finder_process
from shared_memory_dict import SharedMemoryDict
from atexit import register

CAMERAS = load_config("cameras")

class ProcessManager:
    def __init__(self, function, *args, **kwargs):
        self.function = function
        self.process = Process(target=self.function, args=args, kwargs=kwargs)

    def start(self):
        self.process.start()

    def stop(self):
        self.process.terminate()
        self.process.join()

    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, *args):
        self.stop()

class ProcessesManager:
    def __init__(self, function, num_processes):
        self.function = function
        self.num_processes = num_processes
        self.pool = Pool(self.num_processes)
        self.starmap = None

    def start(self, args):
        self.starmap = self.pool.starmap_async(self.function, args)

    def stop(self):
        self.pool.close()
        self.pool.join()

    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, *args):
        self.stop()

class FinderManager(ProcessesManager):
    def __init__(self, camera_configs):
        super().__init__(start_finder_process, len(camera_configs.keys()))

        self.camera_configs = camera_configs
        self.shared_memory = {}

        register(self.on_exit)

    def start(self):
        args = []
        for camera_port in self.camera_configs.keys():
            share_settings = {
                "name": f"finder_{camera_port}_data",
                "size": 1000000
            }

            self.shared_memory[camera_port] = SharedMemoryDict(**share_settings)
            self.shared_memory[camera_port]["tags"] = []

            args.append((int(camera_port), self.camera_configs[camera_port], share_settings))

        super().start(args)
    
    def on_exit(self):
        for camera_port in self.camera_configs.keys():
            memory = self.shared_memory[camera_port]
            memory.close()
            memory.unlink()
        self.shared_memory = {}