from config import load_config
from numpy import ndarray, array
from shared_memory_dict import SharedMemoryDict
from time import time, sleep
from platform_constants import cv2_backend
from wpimath.geometry import Pose3d, Rotation3d, Translation3d, Quaternion

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
        self.camera_pose = camera_config["pose"]
        self.camera_pose = Pose3d(Translation3d(self.camera_pose["translation"]["x"], self.camera_pose["translation"]["y"], self.camera_pose["translation"]["z"]),
                                  Rotation3d(Quaternion(self.camera_pose["rotation"]["quaternion"]["W"], self.camera_pose["rotation"]["quaternion"]
                                             ["X"], self.camera_pose["rotation"]["quaternion"]["Y"], self.camera_pose["rotation"]["quaternion"]["Z"])))

        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_config["width"])
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT,
                        self.camera_config["height"])
        self.stream.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
        self.stream.set(cv2.CAP_PROP_FPS, self.camera_config["fps"])

        self.previous_time = time()

    def process_apriltag(self, tag):
        est = self.estimator.estimateOrthogonalIteration(
            tag, DETECTION_ITERATIONS)
        return {"tag": tag, "pose": est.pose1}

    def find(self, frame: ndarray) -> list[dict]:
        """Find the tags in the frame."""

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        tags = self.remove_errors(self.detector.detect(gray))
        estimates = [self.process_apriltag(tag) for tag in tags]

        return estimates

    def solve(self, estimates: list[dict]) ->  Pose3d:
        """Solves for the position of the robot on the field. It is weighted by the decision margin of the tag."""

        robot_estimated_poses = []
        robot_weights = []
        for estimate in estimates:
            tag = estimate["tag"]
            tag_estimate = estimate["pose"]

            tag_field_pose = self.field.getTagPose(tag.getId())

            tag_estimate_pose = Pose3d(
                tag_estimate.rotation(), tag_estimate.translation())
            robot_estimate_pose = self.robot_pose(tag_estimate_pose, tag_field_pose)

            robot_estimated_poses.append(robot_estimate_pose)
            robot_weights.append(tag.getDecisionMargin())

        if len(robot_estimated_poses) == 0:
            return None
        
        robot_pose = self.weighted_average(
            robot_estimated_poses, robot_weights)
        
        return robot_pose


    def robot_pose(self, tag_estimate_pose: Pose3d, tag_field_pose: Pose3d) -> Pose3d:
        cam_estimate_rel_pose = tag_estimate_pose * -1
        cam_relto_pose = cam_estimate_rel_pose.relativeTo(
            tag_estimate_pose).translation / 2.0

        cam_relto_x = -cam_relto_pose.X()
        cam_relto_y = cam_relto_pose.Y()
        cam_relto_z = -cam_relto_pose.Z()

        cam_angle = tag_field_pose.rotation() - cam_estimate_rel_pose.rotation()

        cam_fcs_abs = Pose3d(Translation3d(cam_relto_x+tag_field_pose.X(), cam_relto_y+tag_field_pose.Y(),
                                           cam_relto_z+tag_field_pose.Z()), cam_angle)
        
        cam_fcs_abs_x = cam_fcs_abs.X()
        cam_fcs_abs_y = cam_fcs_abs.Y()
        cam_fcs_abs_z = cam_fcs_abs.Z()

        robot_angle = cam_fcs_abs.rotation() + self.camera_pose.rotation()

        robot_fcs_abs = Pose3d(Translation3d(cam_fcs_abs_x+self.camera_pose.X(), cam_fcs_abs_y+self.camera_pose.Y(),
                                                cam_fcs_abs_z+self.camera_pose.Z()), robot_angle)
        
        return robot_fcs_abs
    
    def weighted_average(self, poses: list[Pose3d], weights: list[float]) -> Pose3d:
        """Get the weighted average of the poses position and rotation. The weight applys to each individual pose."""
            
        translation = Translation3d()
        rotation = Rotation3d()

        for i, pose in enumerate(poses):
            translation += pose.translation() * weights[i]
            rotation += pose.rotation() * weights[i]

        translation /= sum(weights)
        rotation /= sum(weights)

        return Pose3d(translation, rotation)

    def remove_errors(self, tags: list[apriltag.AprilTagDetection]) -> None:
        """Remove the tags that are not valid."""

        return [tag for tag in tags if tag.getDecisionMargin() > DECISION_MARGIN]

    def run(self) -> None:
        """Run the finder in a loop."""

        while 1:
            time_elapsed = time() - self.previous_time
            sleep(max(0, 1 / self.camera_config["fps"] - time_elapsed))
            alive, frame = self.stream.read()

            if not alive:
                break

            found_tags = self.find(frame)
            robot_pose = self.solve(found_tags)

            if robot_pose is not None:
                quaternion = robot_pose.rotation().getQuaternion()
                self.shared_dict["pose"] = {"translation":{"x": robot_pose.X(), "y": robot_pose.Y(), "z": robot_pose.Z()},
                                            "quaternion": {"W": quaternion.W(), "X": quaternion.X(), "Y": quaternion.Y(), "Z": quaternion.Z()}}
                self.shared_dict["time"] = time()

            self.previous_time = time()


def start_finder_process(camera_port: int, camera_config: dict, share_settings: dict) -> None:
    """Start the finder process."""

    camera_config["port"] = camera_port
    shared_dict = SharedMemoryDict(**share_settings)
    finder = Finder(camera_config, shared_dict)
    finder.run()
