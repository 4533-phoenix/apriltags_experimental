from config import load_config
from numpy import ndarray, array
from pupil_apriltags import Detector, Detection
from multiprocessing.connection import PipeConnection
from threading import Thread
from time import time, sleep
from platform_constants import cv2_backend

import cv2

# Load the config files
ENVIROMENT = load_config("enviroment")
CONFIG = load_config("config")

used_tag_families = set([tag["tag_family"] for tag in ENVIROMENT["tags"].values()])
used_ids = set(ENVIROMENT["tags"].keys())

class FinderOutput(dict):
    def __init__(self, child_pipe: PipeConnection) -> None:
        """Initialize the finder output."""

        super().__init__()
        self.child_pipe = child_pipe

        self["detections"] = []
        self["status"] = "created"
        self["valid"] = False
        
        self.last_checked = time()

        self.checking = True
        self.sending = True

        self.sender = Thread(target=self.send_thread, daemon=True, name="Sender")
        self.sender.start()

        self.checker = Thread(target=self.check_thread, daemon=True, name="Checker")
        self.checker.start()

    def check(self) -> None:
        """Check if the output is valid."""

        if self["status"] == "running" and time() - self.last_checked < 0.5:
            self["valid"] = True
        else:
            self["valid"] = False

    def check_thread(self) -> None:
        """Check if the output is valid in a thread."""

        while self.checking:
            self.check()

            sleep(0.1)

    def send(self) -> None:
        """Send the output to the child pipe."""

        self.child_pipe.send(dict(self))

    def send_thread(self) -> None:
        """Send the output to the child pipe in a thread."""

        while self.sending:
            self.send()
            sleep(0.1)

    def set_status(self, status: str, valid: bool) -> None:
        """Set the status of the output."""

        self["status"] = status
        self["valid"] = valid

    def set_data(self, frame: ndarray, detections: list[Detection]) -> None:
        """Set the data of the output."""

        self["detections"] = detections

    def __delete__(self, instance) -> None:
        """Delete the output."""

        self.checking = False
        self.sending = False

        self.checker.join()
        self.sender.join()

    def __setitem__(self, key, value):
        self.last_checked = time()
        super().__setitem__(key, value)

class Finder:
    def __init__(self, camera_config: dict, child_pipe: PipeConnection) -> None:
        """Initialize the finder class."""

        self.camera_config = camera_config
        self.child_pipe = child_pipe

        self.stream = cv2.VideoCapture(self.camera_config["port"], cv2_backend)
        self.calibration = load_config("calibrations/" + self.camera_config["type"])

        self.detector = Detector(
            **self.calibration["detector"],
            **{"families": " ".join(used_tag_families), "debug": 0}
        )
        
        self.camera_matrix = array(self.calibration["camera_matrix"])
        self.camera_params = (
            self.camera_matrix[0, 0],
            self.camera_matrix[1, 1],
            self.camera_matrix[0, 2],
            self.camera_matrix[1, 2]
        )

        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_config["width"])
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_config["height"])
        self.stream.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
        self.stream.set(cv2.CAP_PROP_FPS, self.camera_config["fps"])

        self.output = FinderOutput(self.child_pipe)
        self.previous_time = time()

    def find(self, frame: ndarray) -> list[dict]:
        """Find the tags in the frame."""

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        tags = self.detector.detect(
            frame, estimate_tag_pose=True, camera_params=self.camera_params, tag_size=ENVIROMENT["tag_size"])
        return tags

    def remove_errors(self, tags: list[Detection]) -> None:
        """Remove the tags that are not in the enviroment, have a high hamming distance, or pose error."""

        return [tag for tag in tags if str(tag.tag_id) in used_ids and tag.tag_family.decode() in used_tag_families and tag.hamming <= 1 and tag.pose_err <= 0.0001]

    def run(self) -> None:
        """Run the finder in a loop."""

        self.output.set_status("running", True)

        while 1:
            time_elapsed = time() - self.previous_time
            sleep(max(0, 1 / self.camera_config["fps"] - time_elapsed))
            alive, frame = self.stream.read()

            if not alive:
                self.output.set_status("stopped", False)
                break

            found_tags = self.remove_errors(self.find(frame))
            self.output.set_data(found_tags)
            self.previous_time = time()

def start_finder_process(camera_port: int, camera_config: dict, parent_pipe: PipeConnection) -> None:
    """Start the finder process."""

    camera_config["port"] = camera_port
    finder = Finder(camera_config, parent_pipe)
    finder.run()