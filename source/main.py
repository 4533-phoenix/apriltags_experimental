import viewer.web3d as web_3d_viewer

from process_manager import FinderManager
from argparse import ArgumentParser
from logging import DEBUG, INFO
from solver import solve
from pathlib import Path
from config import load_config
from logger import logger
from os import chdir

import cv2

chdir(Path(__file__).parent.resolve())
CAMERAS = load_config("cameras")
CONFIG = load_config("config")

if __name__ == "__main__":
    parser = ArgumentParser(prog="Apriltag Tracker",
                            description="Apriltag Tracker for FRC")
    parser.add_argument("-i", "--networktable_ip", type=str,
                        default="localhost", help="The IP of the NetworkTable server")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="Enable debug mode")
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(DEBUG)
    else:
        logger.setLevel(INFO)

    logger.info("Starting Apriltag Tracker")

    finder_manager = FinderManager(CAMERAS)
    finder_manager.start()
    
    while 1:
        for camera_port, data in finder_manager.data.items():
            pass