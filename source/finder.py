from config import load_config
from logger import logger

import pupil_apriltags as apriltag
import orjson as json

import numpy
import time
import cv2
import os

CAMERAS = load_config("cameras")
ENVIROMENT = load_config("enviroment")

tag_families = set([tag["tag_family"] for tag in ENVIROMENT["tags"]])

ids = [tag["id"] for tag in ENVIROMENT["tags"]]
ids.append(0)
used_ids = set(ids)

class Finder:
    def __init__(self, camera_index: int) -> None:
        self.camera_index = camera_index

        self.camera = CAMERAS[camera_index]
        self.stream = cv2.VideoCapture(self.camera["port"], cv2.CAP_DSHOW)
        self.calibration = load_config("calibrations/" + self.camera["type"])
        self.detector = apriltag.Detector(**self.calibration["detector"], **{"families": " ".join(tag_families), "debug": 0})
        self.camera_matrix = numpy.array(self.calibration["camera_matrix"])
        self.camera_params = (self.camera_matrix[0, 0], self.camera_matrix[1, 1], self.camera_matrix[0, 2], self.camera_matrix[1, 2])

        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera["width"])
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera["height"])
        self.stream.set(cv2.CAP_PROP_FPS, self.camera["fps"])

        self.previous_time = time.time()

    def find(self, frame: numpy.ndarray) -> list[dict]:
        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        tags = self.detector.detect(grey, estimate_tag_pose=True, camera_params=self.camera_params, tag_size=ENVIROMENT["tag_size"])
        return [{"rotation": numpy.array(tag.pose_R), "transform": numpy.array(tag.pose_t), "error": tag.pose_err, "family": tag.tag_family.decode(), "id": tag.tag_id} for tag in self.remove_errors(tags)]

    def solve(self, tags: list[dict]):
        pass
    # def draw(self, frame, tags):
    #     for tag in tags:
    #         (ptA, ptB, ptC, ptD) = tag.corners
    #         ptB = (int(ptB[0]), int(ptB[1]))
    #         ptC = (int(ptC[0]), int(ptC[1]))
    #         ptD = (int(ptD[0]), int(ptD[1]))
    #         ptA = (int(ptA[0]), int(ptA[1]))
    #         cv2.line(frame, ptA, ptB, (0, 255, 0), 2)
    #         cv2.line(frame, ptB, ptC, (0, 255, 0), 2)
    #         cv2.line(frame, ptC, ptD, (0, 255, 0), 2)
    #         cv2.line(frame, ptD, ptA, (0, 255, 0), 2)
    #         (cX, cY) = (int(tag.center[0]), int(tag.center[1]))
    #         cv2.circle(frame, (cX, cY), 5, (0, 0, 255), -1)
    #         tagFamily = tag.tag_family.decode("utf-8")
    #         cv2.putText(frame, tagFamily, (ptA[0], ptA[1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    def remove_errors(self, tags: apriltag.Detection) -> None:
        return [tag for tag in tags if tag.tag_id in used_ids and tag.tag_family.decode() in tag_families]

    def run(self) -> None:
        while True:
            time_elapsed = time.time() - self.previous_time
            time.sleep(max(0, 1 / self.camera["fps"] - time_elapsed))
            alive, frame = self.stream.read()

            if not alive:
                logger.warning(f"Camera {self.camera_index} is disconnected")
                break

            found_tags = self.find(frame)
            solved_position = self.solve(found_tags)
            self.previous_time = time.time()
