import pupil_apriltags as apriltags

import numpy
import yaml
import math
import cv2

tag_size = (85) / 1000  # in mm

def putLines(img, text, org, fontFace, fontScale, thickness=..., *args, **kwargs):
    for index, line in enumerate(text.split("\n")):
        (labelWidth, labelHeight), baseline = cv2.getTextSize(
            line, fontFace, fontScale, thickness)
        cv2.putText(img, line, org=(org[0] - round(labelWidth / 2), org[1] + (labelHeight * (
            index + 1))), fontFace=fontFace, fontScale=fontScale, thickness=thickness, *args, **kwargs)


def convertToMeters(position):
    x = position[0]
    y = position[1]
    z = position[2]

    position[0] = x
    position[1] = y
    position[2] = z

    return position


detector = apriltags.Detector(searchpath=['apriltags'],
                              families='tag36h11',
                              nthreads=4,
                              quad_decimate=1.0,
                              quad_sigma=0.0,
                              refine_edges=1,
                              decode_sharpening=0.25,
                              debug=0)
camera_type = "lifecam"
camera = cv2.VideoCapture(0)

with open(f'./calibration/cameras/{camera_type}_calibration.yaml', 'r') as stream:
    parameters = yaml.safe_load(stream)

camera_matrix = numpy.array(parameters['camera_matrix'])
camera_params = (camera_matrix[0, 0], camera_matrix[1, 1],
                 camera_matrix[0, 2], camera_matrix[1, 2])

positions_x = []
positions_z = []

while True:
    ret, frame = camera.read()

    grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    array = cv2.convertScaleAbs(grey)

    tags = detector.detect(array, estimate_tag_pose=True,
                           camera_params=camera_params, tag_size=tag_size)

    for tag in tags:
        tag_visual_size = math.sqrt(
            (tag.corners[0][0] - tag.center[0])**2 + (tag.corners[0][1] - tag.center[1])**2)
        tag_position_meters = convertToMeters(
            list(map(float, tag.pose_t.round(decimals=4))))

        for idx in range(len(tag.corners)):
            cv2.line(frame, tuple(
                tag.corners[idx-1, :].astype(int)), tuple(tag.corners[idx, :].astype(int)), (0, 255, 0))

        #org=(round(tag.center[0]), round(
        #             tag.center[1] + tag_visual_size)),

        putLines(frame, f'ID: {str(tag.tag_id)}\nPosition: {str(tag_position_meters)}',
                 org=(300, 300),
                 fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                 fontScale=0.8,
                 color=(0, 0, 255),
                 thickness=2)
    if (tags):
        positions_x.append(tags[0].pose_t[0])
        positions_z.append(tags[0].pose_t[2])

    # Display the resulting frame
    cv2.namedWindow('frame', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
    cv2.imshow('frame', frame)

    # the 'q' button is set as the
    # quitting button you may use any
    # desired button of your choice
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break