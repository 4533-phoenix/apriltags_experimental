import viewer.viewer as viewer

from config import load_config
from logger import logger

import threading
import argparse
import logging
import finder
import solver
import cv2

CAMERAS = load_config("cameras")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Apriltag Tracker",
                                     description="Apriltag Tracker for FRC")
    parser.add_argument("-i", "--networktable_ip", type=str,
                        default="localhost", help="The IP of the NetworkTable server")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="Enable debug mode")
    args = parser.parse_args()

    if args.debug: logger.setLevel(logging.DEBUG)
    else: logger.setLevel(logging.INFO)

    logger.info("Starting Apriltag Tracker")

    apriltag_finders = []
    for camera_index in range(len(CAMERAS)):
        f = finder.Finder(camera_index)
        t = threading.Thread(target=f.run, daemon=True, name=f"Finder {camera_index}", args=())

        apriltag_finders.append({"thread": t, "class": f})
        t.start()
    viewer.thread_start()

    while threading.active_count() > 0:
        finder_objects = [f["class"] for f in apriltag_finders if f["thread"].is_alive()]

        for finder_object in finder_objects:
            try:
                frame = finder_object.output["frame"]["data"]
                finder_object.draw(frame, finder_object.output["tags"])
                cv2.imshow(f"Camera {finder_object.camera_index}", frame)
            except:
                pass
        cv2.waitKey(1)

        tm = solver.solve(finder_objects)
        viewer.tm = tm