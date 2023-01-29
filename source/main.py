import viewer.local as localViewer
import viewer.web as webViewer

from multiprocessing import Process, Pipe
from argparse import ArgumentParser
from logging import DEBUG, INFO
from finder import start_finder
from solver import solve
from pathlib import Path
from config import load_config
from logger import logger
from time import time
from os import chdir

import cv2

CAMERAS = load_config("cameras")
chdir(Path(__file__).parent.resolve())

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

    apriltag_processes = []
    for camera_index in range(len(CAMERAS)):
        parent_pipe, child_pipe =  Pipe()
        proc = Process(target=start_finder, args=(child_pipe,))

        parent_pipe.send(camera_index)
        proc.start()

        apriltag_processes.append({"process": proc, "pipe": parent_pipe, "camera_index": camera_index, "output": None, "last_output": time()})

    webViewer.thread_start()

    while 1:
        dead_processes = []
        solver_input = []

        for process_index, apriltag_process in enumerate(apriltag_processes):
            if apriltag_process["process"].is_alive():
                if apriltag_process["pipe"].poll():
                    new_output = apriltag_process["pipe"].recv()
                    if new_output is not None:
                        apriltag_process["last_output"] = time()
                        apriltag_process["output"] = new_output
                else:
                    if time() - apriltag_process["last_output"] > 0.5:
                        apriltag_process["output"] = None
                        continue

                if apriltag_process["output"] is not None:
                    solver_input.append({"camera_index": apriltag_process["camera_index"], "output": apriltag_process["output"]})

                    frame = apriltag_process["output"]["frame"]["data"]
                    tags = apriltag_process["output"]["tags"]

                    if frame is None:
                        continue

                    cv2.namedWindow(f"Camera {apriltag_process['camera_index']}", cv2.WINDOW_NORMAL)
                    cv2.resizeWindow(f"Camera {apriltag_process['camera_index']}", 640, 480)
                    cv2.imshow(f"Camera {apriltag_process['camera_index']}", localViewer.draw(frame, tags))
            else:
                apriltag_processes["outpt"] = None
                dead_processes.append(process_index)
                continue

            cv2.waitKey(1)

        for process_index in dead_processes:
            logger.error(f"Apriltag process {apriltag_processes[process_index]['camera_index']} died")
            apriltag_processes.pop(process_index)

        tm = solve(solver_input)
        webViewer.tm = tm