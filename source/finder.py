from config import load_config
from numpy import ndarray, array
from shared_memory_dict import SharedMemoryDict
from time import time, sleep
from platform_constants import cv2_backend
from wpimath.geometry import Pose3d, Rotation3d, Translation3d
from viewer.webmjpeg import MjpegViewer
from viewer.draw import draw
from math import pi, degrees

import robotpy_apriltag as apriltag
import cv2

# Load the config files
CONFIG = load_config("config")
FIELD = CONFIG["config"]["field"]

FIELD_TAGS = load_config("fields/" + FIELD + "-tag.json")
DECISION_MARGIN = FIELD_TAGS["decision_margin"]
DETECTION_ITERATIONS = FIELD_TAGS["detection_iterations"]

FIELD_LAYOUT = load_config("fields/" + FIELD + ".json")


class Finder:
    def __init__(self, camera_config: dict, shared_dict: SharedMemoryDict) -> None:
        """Initialize the finder class."""

        self.camera_config = camera_config
        self.shared_dict = shared_dict

        self.stream = cv2.VideoCapture(self.camera_config["port"], cv2_backend)
        self.calibration = load_config(
            "calibrations/" + self.camera_config["type"])

        self.detector = apriltag.AprilTagDetector()
        self.detector.addFamily(FIELD_TAGS["family"])

        self.camera_matrix = array(self.calibration["camera_matrix"])
        self.estimator = apriltag.AprilTagPoseEstimator(
            apriltag.AprilTagPoseEstimator.Config(
                # 0.2, 500, 500, frame_size[1] / 2.0, frame_size[0] / 2.0 # orig not for HD3000, might be picam?
                FIELD_TAGS["size"], *(self.camera_matrix[0, 0], self.camera_matrix[1, 1], self.camera_matrix[0,
                                      2], self.camera_matrix[1, 2])  # from wpiilbjExamples HD3000 config values
            )
        )

        self.field = apriltag.AprilTagFieldLayout(
            FIELD["tags"], FIELD["field"]["length"], FIELD["field"]["width"])

        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_config["width"])
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT,
                        self.camera_config["height"])
        self.stream.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
        self.stream.set(cv2.CAP_PROP_FPS, self.camera_config["fps"])

        if CONFIG["features"]["webmjpeg_viewer"]["enabled"]:
            self.mjpeg = MjpegViewer(int(self.camera_config["port"]), int(
                CONFIG["features"]["webmjpeg_viewer"]["starting_port"]))
            self.mjpeg.start()
        else:
            self.mjpeg = None

        self.previous_time = time()

    def process_apriltag(self, tag):
        est = self.estimator.estimateOrthogonalIteration(
            tag, DETECTION_ITERATIONS)
        return {"tag": tag, "estimate": est.pose1}

    def find(self, frame: ndarray) -> list[dict]:
        """Find the tags in the frame."""

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        tags = self.remove_errors(self.detector.detect(gray))
        poses = [self.process_apriltag(tag) for tag in tags]

        return poses

    def solve(self, poses: list[dict]) -> list[dict]:
        """Solves for the position of the robot on the field. It is weighted by the decision margin of the tag."""

        transformations = []
        for pose in poses:
            tag = pose["tag"]
            tag_estimate = pose["estimate"]

            known_pose = self.field.getTagPose(tag.getId())

            tag_estimate_pose_rotation = tag_estimate.rotation()
            tag_estimate_pose_translation = tag_estimate.translation()

            tag_estimate_pose = Pose3d(
                tag_estimate_pose_rotation, tag_estimate_pose_translation)
            camera_pose = self.tagposeToCameraPosition(
                tag_estimate_pose, known_pose)

    def tagposeToCameraPosition(self, tag_estimate_pose, known_pose):
        tag_atc_rel_pose = tag_estimate_pose
        cam_atc_rel_rot = -tag_atc_rel_pose.rotation()
        cam_atc_rel_transl = -tag_atc_rel_pose.translation()
        cam_atc_rel_pose = Pose3d(cam_atc_rel_transl, cam_atc_rel_rot)
        temppose = cam_atc_rel_pose.relativeTo(tag_atc_rel_pose)
        x = -temppose.Z()/2.0
        y = temppose.X()/2.0
        z = -temppose.Y()/2.0
        cameraZangle = known_pose.rotation().Z() + pi - cam_atc_rel_rot.Y()
        # cam_fcs_rel = Pose3d(Translation3d(x, y, z),
        #                      Rotation3d(0, 0, cameraZangle))
        cam_fcs_abs = Pose3d(Translation3d(x+known_pose.X(), y+known_pose.Y(),
                             z+known_pose.Z()), Rotation3d(0, 0, cameraZangle))
        # xr, yr, zr = cam_fcs_rel.translation().X(
        # ), cam_fcs_rel.translation().Y(), cam_fcs_rel.translation().Z()
        xa, ya, za = cam_fcs_abs.translation().X(
        ), cam_fcs_abs.translation().Y(), cam_fcs_abs.translation().Z()
        cameraZangleDeg = degrees(cameraZangle)
        
        return {
            "heading": cameraZangleDeg,
            "absolute": {
                "x": xa,
                "y": ya,
                "z": za
            }
        }

    def remove_errors(self, tags: list[apriltag.AprilTagDetection]) -> None:
        """Remove the tags that are not in the ENVIRONMENT, have a high hamming distance, or pose error."""

        return [tag for tag in tags if tag.getDecisionMargin() > DECISION_MARGIN]

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

            self.shared_dict["tags"] = {tag.tag_id: transformations.transform_from(
                array(tag.pose_R), array(tag.pose_t).flatten()) for tag in found_tags}
            self.previous_time = time()


def start_finder_process(camera_port: int, camera_config: dict, share_settings: dict) -> None:
    """Start the finder process."""

    camera_config["port"] = camera_port
    shared_dict = SharedMemoryDict(**share_settings)
    finder = Finder(camera_config, shared_dict)
    finder.run()
