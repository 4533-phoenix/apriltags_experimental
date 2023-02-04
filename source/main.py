from process_manager import FinderManager
from logging import DEBUG, INFO
from solver import solve
from pathlib import Path
from config import load_config
from logger import logger
from os import chdir
from numpy import array

import cv2

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

    if CONFIG["features"]["web3d_viewer"]["enabled"]:
        import viewer.web3d as web_3d_viewer
        web_3d_viewer.thread_start()

        ENVIROMENT = load_config("enviroment")

        for tag_id, tag in ENVIROMENT["tags"].items():
            web_3d_viewer.transformations[f"tag_{tag_id}"] = list(array(tag["transformation"]).flatten())
    
    while 1:
        solved = solve(finder_manager.data)
        if solved and CONFIG["features"]["web3d_viewer"]["enabled"]:
            web_3d_viewer.transformations["robot"] = list(solved["transformation"].flatten())