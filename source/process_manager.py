from config import load_config
from multiprocessing.pool import Pool
from multiprocessing import Process
from finder import start_finder_process
from shared_memory_dict import SharedMemoryDict
from networktable import start_networktable_process
from atexit import register
from typing import Self

CAMERAS = load_config("cameras")

class ProcessManager:
    def __init__(self, function, *args, **kwargs) -> None:
        """Initialize the processes manager class."""

        self.function = function
        self.process = Process(target=self.function, args=args, kwargs=kwargs)

    def start(self) -> None:
        """Start the processes manager."""

        self.process.start()

    def stop(self) -> None:
        """Stop the processes manager."""

        self.process.terminate()
        self.process.close()
        self.process.join()

    def __enter__(self) -> Self:
        """Start the processes manager on enter."""

        self.start()
        return self
    
    def __exit__(self, *args) -> None:
        """Stop the processes manager on exit."""

        self.stop()

class ProcessesManager:
    def __init__(self, function, num_processes) -> None:
        """Initialize the processes manager class."""

        self.function = function
        self.num_processes = num_processes
        self.pool = Pool(self.num_processes)
        self.starmap = None

    def start(self, args) -> None:
        """Start the processes manager."""

        self.starmap = self.pool.starmap_async(self.function, args)

    def stop(self) -> None:
        """Stop the processes manager."""

        self.pool.terminate()
        self.pool.close()
        self.pool.join()

    def __enter__(self) -> Self:
        """Start the processes manager on enter."""

        self.start()
        return self
    
    def __exit__(self, *args) -> None:
        """Stop the processes manager on exit."""

        self.stop()

class FinderManager(ProcessesManager):
    def __init__(self, camera_configs) -> None:
        """Initialize the finder manager class."""

        super().__init__(start_finder_process, len(camera_configs.keys()))

        self.camera_configs = camera_configs
        self.shared_memory = {}

        register(self.on_exit)

    def start(self) -> None:
        """Start the finder manager."""

        args = []
        for camera_port in self.camera_configs.keys():
            share_settings = {
                "name": f"finder_{camera_port}_data",
                "size": 1000000
            }

            self.shared_memory[camera_port] = SharedMemoryDict(**share_settings)
            self.shared_memory[camera_port]["tags"] = {}

            args.append((int(camera_port), self.camera_configs[camera_port], share_settings))

        super().start(args)
    
    def on_exit(self) -> None:
        """Close the shared memory on exit."""

        for camera_port in self.camera_configs.keys():
            memory = self.shared_memory[camera_port]
            memory.close()
            memory.unlink()
        self.shared_memory = {}

class NetworkTableManager(ProcessManager):
    def __init__(self) -> None:
        """Initialize the network table manager class."""
        
        self.shared_memory = SharedMemoryDict(name="network_table_data", size=1000000)
        
        super().__init__(start_networktable_process, self.shared_memory)

        register(self.on_exit)

    def on_exit(self) -> None:
        """Close the shared memory on exit."""
        self.shared_memory.close()
        self.shared_memory.unlink()
        self.shared_memory = {}

    def update(self, solved_position):
        """Update the network table data."""
        self.shared_memory["position"] = solved_position["position"]
        self.shared_memory["rotation"] = solved_position["rotation"]
        self.shared_memory["transformation"] = solved_position["transformation"]