from process_manager import FinderManager, NetworkTableManager
from logging import DEBUG, INFO
from pathlib import Path
from config import load_config
from os import chdir

chdir(Path(__file__).parent.resolve())
CAMERAS = load_config("cameras")
CONFIG = load_config("config")

if __name__ == "__main__":
    finder_manager = FinderManager(CAMERAS)
    finder_manager.start()

    networktable_manager = NetworkTableManager()
    networktable_manager.start()
    
    while 1:
        camera_detections = {}
        for camera_port, shared_memory in finder_manager.shared_memory.items():
            camera_detections[camera_port] = shared_memory["tags"]
            
# robot = win