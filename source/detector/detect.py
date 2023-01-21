import os
os.environ["OPENCV_LOG_LEVEL"] = "SILENT"

import cv2
import climage


def list_ports():
    """
    Test the ports and returns a tuple with the available ports and the ones that are working.
    """
    non_working_ports = []
    working_ports = []
    available_ports = []
    dev_port = 0
    # if there are more than 5 non working ports stop the testing.
    while len(non_working_ports) < 6:
        camera = cv2.VideoCapture(dev_port, cv2.CAP_DSHOW)
        if not camera.isOpened():
            non_working_ports.append(dev_port)
        else:
            is_reading, img = camera.read()
            w = camera.get(3)
            h = camera.get(4)
            if is_reading:
                print("Port %s is working and reads images (%s x %s)" %
                      (dev_port, h, w))

                cv2.imwrite("temp.jpg", img)
                print("Image looks like this:")
                print(climage.convert("temp.jpg"))
                os.remove("temp.jpg")

                working_ports.append(dev_port)
            else:
                print("Port %s for camera ( %s x %s) is present but does not reads." % (
                    dev_port, h, w))
                available_ports.append(dev_port)
        dev_port += 1
    return available_ports, working_ports, non_working_ports


connected_ports = list_ports()[1]
print("Connected ports: %s" % connected_ports)
