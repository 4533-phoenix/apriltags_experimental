from config import load_config
from pytransform3d import rotations
from pytransform3d import transformations
from pytransform3d import transform_manager
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
    tm = transform_manager.TransformManager()

    for camera_port, detections in data.items():
        camera = CAMERAS[camera_port]
        robot_to_camera = array(camera["transformation"])
        camera_to_robot = transformations.invert_transform(robot_to_camera)

        tm.add_transform("robot", f"camera-{camera_port}", robot_to_camera)

        for tag_id, tag_transformation in detections.items():
            tag_data = ENVIROMENT["tags"][str(tag_id)]
            tag_size = ENVIROMENT["tag_size"]

            field_to_tag = array(tag_data["transformation"]).reshape(4, 4)
            camera_to_tag = array(tag_transformation).reshape(4, 4)

            camera_to_tag[:3, 3] *= tag_size
            camera_to_tag[:3, 3] = [camera_to_tag[1, 3], camera_to_tag[0, 3], camera_to_tag[2, 3]]

            try:
                tm.add_transform(f"camera-{camera_port}", f"tag-{tag_id}", camera_to_tag)
                tm.add_transform("field", f"tag-{tag_id}", field_to_tag)
            except:
                continue

    if not tm.has_frame("field"):
        return None
    
    average_transformation = tm.get_transform("field", "robot")

    # convert the transformation to a dictionary
    return {
        "position": average_transformation[:3, 3],
        "rotation": rotation_matrix_to_compact_euler_angles(average_transformation[:3, :3]),
        "transformation": average_transformation,
        "manager": tm,
    }