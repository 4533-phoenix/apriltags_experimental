from pupil_apriltags import Detection
from numpy import ndarray

import cv2

def draw(frame: ndarray, tags: list[Detection]) -> ndarray:
    for tag in tags:
        (ptA, ptB, ptC, ptD) = tag.corners
        ptB = (int(ptB[0]), int(ptB[1]))
        ptC = (int(ptC[0]), int(ptC[1]))
        ptD = (int(ptD[0]), int(ptD[1]))
        ptA = (int(ptA[0]), int(ptA[1]))
        cv2.line(frame, ptA, ptB, (0, 255, 0), 2)
        cv2.line(frame, ptB, ptC, (0, 255, 0), 2)
        cv2.line(frame, ptC, ptD, (0, 255, 0), 2)
        cv2.line(frame, ptD, ptA, (0, 255, 0), 2)
        (cX, cY) = (int(tag.center[0]), int(tag.center[1]))
        cv2.circle(frame, (cX, cY), 5, (255, 0, 255), -1)
        cv2.circle(frame, ptA, 5, (255, 0, 0), -1)
        tagFamily = tag.tag_family.decode("utf-8")
        cv2.putText(frame, tagFamily, (ptA[0], ptA[1] - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # blue crosshair in the center of the screen based on frame size
    cv2.line(frame, (int(frame.shape[1] / 2) - 10, int(frame.shape[0] / 2)), (int(frame.shape[1] / 2) + 10, int(frame.shape[0] / 2)), (255, 0, 0), 2)
    cv2.line(frame, (int(frame.shape[1] / 2), int(frame.shape[0] / 2) - 10), (int(frame.shape[1] / 2), int(frame.shape[0] / 2) + 10), (255, 0, 0), 2)

    return frame