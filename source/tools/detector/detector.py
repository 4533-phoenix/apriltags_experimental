import os; os.environ["OPENCV_LOG_LEVEL"] = "SILENT"

import climage
import argparse
import cv2

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scan for usable camera ports.")
    parser.add_argument("-m", "--max-non-working-ports", help="maximum number of non-working ports to scan", default=6, type=int)
    args = parser.parse_args()

    non_working_ports = 0
    current_port = 0

    print("Scanning for working camera ports...")

    while non_working_ports < args.max_non_working_ports:
        camera = cv2.VideoCapture(current_port, cv2.CAP_DSHOW)

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
                print(climage.convert("temp.jpg"))
                os.remove("temp.jpg")
            else:
                print("Port %s for camera ( %s x %s) is present but does not reads." % (
                    current_port, h, w))

        current_port += 1

    print("Done.")