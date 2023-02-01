import viewer.local as localViewer
import viewer.web as webViewer

from threading import Thread, active_count
from argparse import ArgumentParser
from logging import DEBUG, INFO
from finder import Finder
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

    apriltag_finders = []
    for camera_index in range(len(CAMERAS)):
        f = Finder(camera_index)
        t = Thread(target=f.run, daemon=True,
                   name=f"Finder {camera_index}", args=())

        apriltag_finders.append({"thread": t, "class": f})
        t.start()
    if CONFIG["enable_web_viewer"]: webViewer.thread_start()

    while active_count():
        finder_objects = [f["class"]
                          for f in apriltag_finders if f["thread"].is_alive()]

        for finder_object in finder_objects:
            if CONFIG["enable_local_viewer"]:
                try:
                    frame = localViewer.draw(
                        finder_object.output["frame"]["data"], finder_object.output["tags"])

                    name = f"Camera {finder_object.camera_index}"
                    cv2.namedWindow(name, cv2.WINDOW_NORMAL)
                    cv2.imshow(name, frame)
                except:
                    pass
        if CONFIG["enable_local_viewer"]: cv2.waitKey(1)

        tm = solve(finder_objects)
        if CONFIG["enable_web_viewer"]: webViewer.tm = tm
