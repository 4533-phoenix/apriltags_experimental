from config import load_config
from logger import logger

import networktables
import threading
import argparse
import pathlib
import logging
import finder
import numpy
import queue
import time
import math
import cv2
import os

source_path = pathlib.Path(__file__).parent.resolve()
os.chdir(source_path)

CAMERAS = load_config("cameras")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Apriltag Tracker",
                                     description="Apriltag Tracker for FRC")
    parser.add_argument("-i", "--networktable-ip", type=str,
                        default="localhost", help="The IP of the NetworkTable server")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="Enable debug mode")
    args = parser.parse_args()

    if args.debug: logger.setLevel(logging.DEBUG)
    else: logger.setLevel(logging.INFO)

    logger.info("Starting Apriltag Tracker")

    apriltag_finders = {}
    for camera_index in range(len(CAMERAS)):
        f = finder.Finder(camera_index)
        t = threading.Thread(target=f.run, daemon=True, name=f"Finder {camera_index}", args=())

        apriltag_finders.update({camera_index: {"thread": t, "class": f}})
        t.start()

    while threading.active_count() > 0:
        print(apriltag_finders)