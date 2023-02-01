from pathlib import Path; from sys import path; path.append(str(Path(__file__).parent.parent.parent.resolve()))
import os; os.environ["OPENCV_LOG_LEVEL"] = "SILENT"

from climage import convert
from argparse import ArgumentParser
from platform_constants import cv2_backend

import cv2

if __name__ == "__main__":
    parser = ArgumentParser(
        description="Scan for usable camera ports.")
    parser.add_argument("-m", "--max-non-working-ports", help="maximum number of non-working ports to scan", default=6, type=int)
    args = parser.parse_args()

    non_working_ports = 0
    current_port = 0

    print("Scanning for working camera ports...")

    while non_working_ports < args.max_non_working_ports:
        camera = cv2.VideoCapture(current_port, cv2_backend)

        if not camera.isOpened():
            non_working_ports += 1
        else:
            alive, img = camera.read()
            w = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            h = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
            camera.release()

            if alive:
                print("Port %s is working and reads images (%s x %s)" %
                      (current_port, h, w))

                cv2.imwrite("temp.jpg", img)
                print("Image looks like this:")
                print(convert("temp.jpg"))
                os.remove("temp.jpg")
            else:
                print("Port %s for camera ( %s x %s) is present but does not reads." % (
                    current_port, h, w))

        current_port += 1

    print("Done.")