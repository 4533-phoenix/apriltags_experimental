import dt_apriltags as apriltags

import numpy
import yaml
import cv2

detector = apriltags.Detector(searchpath=['apriltags'],
                              families='tag36h11',
                              nthreads=4,
                              quad_decimate=1.0,
                              quad_sigma=0.0,
                              refine_edges=1,
                              decode_sharpening=0.25,
                              debug=0)
camera_type = "logitech"
camera = cv2.VideoCapture(0)
tag_size = 0.04  # in meters

with open(f'./calibration/cameras/{camera_type}_calibration.yaml', 'r') as stream:
    parameters = yaml.safe_load(stream)

camera_matrix = numpy.array(parameters['camera_matrix'])
camera_params = (camera_matrix[0, 0], camera_matrix[1, 1],
                 camera_matrix[0, 2], camera_matrix[1, 2])

positions = []

while True:
    ret, frame = camera.read()

    grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    array = cv2.convertScaleAbs(grey)

    tags = detector.detect(array, estimate_tag_pose=True,
                           camera_params=camera_params, tag_size=tag_size)
    for tag in tags:
        for idx in range(len(tag.corners)):
            cv2.line(frame, tuple(
                tag.corners[idx-1, :].astype(int)), tuple(tag.corners[idx, :].astype(int)), (0, 255, 0))

        cv2.putText(frame, str(tag.tag_id),
                    org=(tag.corners[0, 0].astype(int)+10,
                         tag.corners[0, 1].astype(int)+10),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.8,
                    color=(0, 0, 255),
                    thickness=2)

    if len(tags) > 0:
        # print("Position: " + str(tags[0].pose_t))
        # print("Rotation: " + str(tags[0].pose_R))
        positions.append(tuple(map(float, tags[0].pose_t)))

    # Display the resulting frame
    cv2.imshow('frame', frame)

    # the 'q' button is set as the
    # quitting button you may use any
    # desired button of your choice
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

with open('path.txt', 'w') as stream:
    stream.write(str(positions))