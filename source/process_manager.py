from config import load_config
from multiprocessing.pool import Pool
from multiprocessing import Process, Pipe
from threading import Thread
from finder import start_finder_process
from logger import logger
from time import sleep

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

    def start(self, args):
        self.pool.starmap_async(self.function, args)

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
        self.data = {}
        self.pipes = {}

        self.reciever = Thread(target=self.recieve_thread, daemon=True, name="Reciever Thread")
        self.reciever.start()

    def start(self):
        args = []
        for camera_port in self.camera_configs.keys():
            parent_pipe, child_pipe = Pipe()

            self.pipes[camera_port] = parent_pipe
            self.data[camera_port] = {"status": "starting", "valid": False}
            args.append((int(camera_port), self.camera_configs[camera_port], child_pipe))

        super().start(args)

    def get(self, camera_port):
        try:
            if self.pipes[camera_port].poll():
                self.data[camera_port] = self.pipes[camera_port].recv()
        except BrokenPipeError:
            logger.error("Broken Pipe: " + str(camera_port))

            if camera_port in self.data.keys():
                self.data[camera_port]["status"] = "broken"
                self.data[camera_port]["valid"] = False
    
    def get_all(self):
        for camera_index in self.pipes.keys():
            self.get(camera_index)

    def recieve_thread(self):
        while True:
            self.get_all()
            sleep(0.1)