from config import load_config
from numpy import ndarray, array
from pupil_apriltags import Detector, Detection
from shared_memory_dict import SharedMemoryDict
from threading import Thread
from time import time, sleep
from platform_constants import cv2_backend
from viewer.webmjpeg import MjpegViewer
from viewer.draw import draw

import cv2

# Load the config files
ENVIROMENT = load_config("enviroment")
CONFIG = load_config("config")

used_ids = set(ENVIROMENT["tags"].keys())

class Finder:
    def __init__(self, camera_config: dict, shared_dict: SharedMemoryDict) -> None:
        """Initialize the finder class."""

        self.camera_config = camera_config
        self.shared_dict = shared_dict

        self.stream = cv2.VideoCapture(self.camera_config["port"], cv2_backend)
        self.calibration = load_config("calibrations/" + self.camera_config["type"])

        self.detector = Detector(
            **self.calibration["detector"],
            **{"families": ENVIROMENT["tag_family"], "debug": 0}
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

        if CONFIG["features"]["webmjpeg_viewer"]["enabled"]:
            self.mjpeg = MjpegViewer(int(self.camera_config["port"]), int(CONFIG["features"]["webmjpeg_viewer"]["starting_port"]))
            self.mjpeg.start()
        else:
            self.mjpeg = None

        self.previous_time = time()

    def find(self, frame: ndarray) -> list[dict]:
        """Find the tags in the frame."""

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        tags = self.detector.detect(
            frame, estimate_tag_pose=True, camera_params=self.camera_params, tag_size=ENVIROMENT["tag_size"])
        return tags

    def remove_errors(self, tags: list[Detection]) -> None:
        """Remove the tags that are not in the enviroment, have a high hamming distance, or pose error."""

        return [tag for tag in tags if str(tag.tag_id) in used_ids and tag.tag_family.decode() == ENVIROMENT["tag_family"] and tag.hamming <= 1 and tag.pose_err <= 0.0001]

    def run(self) -> None:
        """Run the finder in a loop."""

        while 1:
            time_elapsed = time() - self.previous_time
            sleep(max(0, 1 / self.camera_config["fps"] - time_elapsed))
            alive, frame = self.stream.read()

            if not alive:
                break

            found_tags = self.remove_errors(self.find(frame))

            if self.mjpeg is not None:
                if CONFIG["features"]["webmjpeg_viewer"]["show_detections"]:
                    draw(frame, found_tags)
                self.mjpeg.update_frame(frame)

            self.shared_dict["tags"] = found_tags
            self.previous_time = time()

def start_finder_process(camera_port: int, camera_config: dict, share_settings: dict) -> None:
    """Start the finder process."""

    camera_config["port"] = camera_port
    shared_dict = SharedMemoryDict(**share_settings)
    finder = Finder(camera_config, shared_dict)
    finder.run()