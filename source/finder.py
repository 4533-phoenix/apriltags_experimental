from config import load_config
from logger import logger
from numpy import ndarray, array
from pupil_apriltags import Detector, Detection
from time import time, sleep
from platform_constants import cv2_backend

import cv2

# Load the config files
ENVIROMENT = load_config("enviroment")
CAMERAS = load_config("cameras")

# Create a set of all the tag families and a set of all the tag ids
tag_families = set([tag["tag_family"] for tag in ENVIROMENT["tags"].values()])
used_ids = set(ENVIROMENT["tags"].keys())


class Finder:
    def __init__(self, camera_index: int) -> None:
        """Initialize the finder class."""

        self.camera_index = camera_index

        self.camera = CAMERAS[camera_index]
        self.stream = cv2.VideoCapture(self.camera["port"], cv2_backend)
        self.calibration = load_config("calibrations/" + self.camera["type"])
        self.detector = Detector(
            **self.calibration["detector"], **{"families": " ".join(tag_families), "debug": 0})
        self.camera_matrix = array(self.calibration["camera_matrix"])
        self.camera_params = (
            self.camera_matrix[0, 0], self.camera_matrix[1, 1], self.camera_matrix[0, 2], self.camera_matrix[1, 2])

        self.output = {"tags": [], "frame": {
            "fps": 0, "data": None}, "status": "ready"}

        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera["width"])
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera["height"])
        self.stream.set(cv2.CAP_PROP_CONVERT_RGB, 0)
        self.stream.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
        self.stream.set(cv2.CAP_PROP_FPS, self.camera["fps"])

        self.previous_time = time()

    def find(self, frame: ndarray) -> list[dict]:
        """Find the tags in the frame."""

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        tags = self.detector.detect(
            frame, estimate_tag_pose=True, camera_params=self.camera_params, tag_size=ENVIROMENT["tag_size"])
        return tags

    def remove_errors(self, tags: list[Detection]) -> None:
        """Remove the tags that are not in the enviroment, have a high hamming distance or pose error."""

        return [tag for tag in tags if str(tag.tag_id) in used_ids and tag.tag_family.decode() in tag_families and tag.hamming <= 1 and tag.pose_err <= 0.0001]

    def run(self) -> None:
        """Run the finder in a loop. This is meant to be ran in a thread."""

        self.output["status"] = "running"

        while 1:
            time_elapsed = time() - self.previous_time
            sleep(max(0, 1 / self.camera["fps"] - time_elapsed))
            alive, frame = self.stream.read()

            if not alive:
                logger.warning(f"Camera {self.camera_index} is disconnected")
                self.output = {"tags": [], "frame": {
                    "fps": 0, "data": None}, "status": "disconnected"}
                break

            found_tags = self.remove_errors(self.find(frame))

            self.output["tags"] = found_tags
            self.output["frame"]["fps"] = 1 / (time() - self.previous_time)
            self.output["frame"]["data"] = frame

            self.previous_time = time()
