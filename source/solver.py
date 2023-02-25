from config import load_config
from pytransform3d import rotations
from pytransform3d import transformations
from numpy import array
from math import atan2, sqrt

# Load the config files
ENVIROMENT = load_config("enviroment")
CAMERAS = load_config("cameras")

def rotation_matrix_to_compact_euler_angles(R):
    """Convert a rotation matrix to compact Euler angles.

    Parameters
    ----------
    R : array_like, shape (3, 3)
        Rotation matrix.

    Returns
    -------
    angles : array_like, shape (3,)
        Compact Euler angles.

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Euler_angles#Rotation_matrix
    """
    return array([atan2(R[2, 1], R[2, 2]), atan2(-R[2, 0], sqrt(R[2, 1] ** 2 + R[2, 2] ** 2)), atan2(R[1, 0], R[0, 0])])

def solve(data: dict[list]) -> dict:
    robot_transformations = []

    for camera_port, detections in data.items():
        camera = CAMERAS[camera_port]
        robot_to_camera = array(camera["transformation"])
        camera_to_robot = transformations.invert_transform(robot_to_camera)

        for tag_id, tag_transformation in detections.items():
            tag_data = ENVIROMENT["tags"][str(tag_id)]

            field_to_tag = array(tag_data["transformation"]).reshape(4, 4)
            camera_to_tag = array(tag_transformation).reshape(4, 4)

            # camera coordinates are The coordinate system has the origin at the camera center. The z-axis points from the camera center out the camera lens. The x-axis is to the right in the image taken by the camera, and y is down. The tag's coordinate frame is centered at the center of the tag, with x-axis to the right, y-axis do
            # convert to field coordinates

            # # swap rotation matrix yaw and roll
            # angle = rotations.compact_axis_angle_from_matrix(relative_tag_transform[:3, :3])
            # angle[1], angle[2] = angle[2], angle[1]
            # relative_tag_transform[:3, :3] = rotations.matrix_from_compact_axis_angle(angle)

            camera_to_tag_offset = [camera_to_tag[0, 3], camera_to_tag[1, 3], 0]
            field_to_offset_tag = transformations.concat(field_to_tag, transformations.transform_from(rotations.matrix_from_compact_axis_angle([0, 0, 0]), camera_to_tag_offset))
            field_to_offset_tag_rotation = transformations.rotate_transform(field_to_offset_tag, camera_to_tag[:3, :3])
            field_to_camera = transformations.concat(field_to_offset_tag_rotation, transformations.transform_from(rotations.matrix_from_compact_axis_angle([0, 0, 0]), [-camera_to_tag[3, 3], 0, 0]))

            print(field_to_camera[:3, 3])

            # tag_to_camera = transformations.invert_transform(camera_to_tag)
            # field_to_camera = transformations.concat(field_to_tag, tag_to_camera)
            # robot_to_field = transformations.concat(camera_to_robot, field_to_camera)

            # robot_transformations.append(field_to_robot)

    if len(robot_transformations) == 0:
        return None
    
    # average the transformations using numpy
    average_transformation = array(robot_transformations).mean(axis=0)

    # convert the transformation to a dictionary
    return {
        "position": average_transformation[:3, 3],
        "rotation": rotation_matrix_to_compact_euler_angles(average_transformation[:3, :3])
    }