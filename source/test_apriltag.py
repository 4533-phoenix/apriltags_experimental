import pupil_apriltags as apriltag
import platform_constants
import numpy
import cv2


calibration = {
    "rms": 0.9988944267052078,
    "camera_matrix": [
        [
            966.6755277057727,
            0.0,
            653.9475842729643
        ],
        [
            0.0,
            961.9081217060867,
            377.9848822296369
        ],
        [
            0.0,
            0.0,
            1.0
        ]
    ],
    "dist_coefs": [
        -0.016614142464272563,
        -0.07806374302785261,
        0.007351259188908908,
        -0.0012009467415949136,
        0.09697992917121022
    ],
    "detector": {
        "nthreads": 4,
        "quad_decimate": 2.0,
        "quad_sigma": 1.0,
        "refine_edges": 2,
        "decode_sharpening": 0.25
    }
}

camera_matrix = numpy.array(calibration["camera_matrix"])

camera_params = (
    camera_matrix[0, 0],
    camera_matrix[1, 1],
    camera_matrix[0, 2],
    camera_matrix[1, 2]
)

cap = cv2.VideoCapture(0, platform_constants.cv2_backend)
detector = apriltag.Detector(
    **calibration["detector"], families="tag16h5", debug=0)


def filter_tags(tags):
    return [tag for tag in tags if tag.tag_id in [1] and tag.hamming <= 1 and tag.pose_err <= 0.0001]


def tag_to_string(tag):
    seperator = "=" * 20
    string = f"""
    {seperator}
    Tag ID: {tag.tag_id}
    Tag Family: {tag.tag_family.decode("utf-8")}
    Tag Pose Error: {tag.pose_err}
    Tag Hamming: {tag.hamming}
    Tag Center: {tag.center}
    Tag Corners: {[f"{index} {tuple(corner)}" for index, corner in enumerate(tag.corners)]}
    Tag Pose T: X: {tag.pose_t[0]} Y: {tag.pose_t[1]} Z: {tag.pose_t[2]}
    {seperator}
    """
    return string


while True:
    ret, frame = cap.read()
    detections = filter_tags(detector.detect(cv2.cvtColor(
        frame, cv2.COLOR_BGR2GRAY), estimate_tag_pose=True, camera_params=camera_params, tag_size=0.2032))
    for detection in detections:
        # print(tag_to_string(detection))
        # print(detection.pose_t.flatten())

        # index 0 is left/right
        # index 1 is forwards/backwards
        # index 2 is up/down

        # print(detection.pose_R)
        pass
    cv2.imshow("frame", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
