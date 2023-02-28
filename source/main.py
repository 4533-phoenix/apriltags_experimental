from process_manager import FinderManager, NetworkTableManager
from logging import DEBUG, INFO
from solver import solve
from pathlib import Path
from config import load_config
from logger import logger
from os import chdir, system
from numpy import array

chdir(Path(__file__).parent.resolve())
CAMERAS = load_config("cameras")
CONFIG = load_config("config")

if __name__ == "__main__":
    if CONFIG["config"]["debug"]:
        logger.setLevel(DEBUG)
    else:
        logger.setLevel(INFO)

    logger.info("Starting Apriltag Tracker")

    finder_manager = FinderManager(CAMERAS)
    finder_manager.start()

    networktable_manager = NetworkTableManager()
    networktable_manager.start()
    
    while 1:
        camera_detections = {}
        for camera_port, shared_memory in finder_manager.shared_memory.items():
            camera_detections[camera_port] = shared_memory["tags"]

        solved = solve(camera_detections)

        system("cls")   

        if solved:
            print(f"Position: {solved['position']}")

            networktable_manager.update(solved)