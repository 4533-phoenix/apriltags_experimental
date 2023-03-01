from config import load_config
from pytransform3d import rotations
from pytransform3d import transformations
from pytransform3d import transform_manager
from numpy import array
from math import degrees
import matplotlib.pyplot as plt

# Load the config files
ENVIROMENT = load_config("enviroment")
CAMERAS = load_config("cameras")


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

            try:
                print(camera_to_tag[:3, 3])
                camera_to_tag[:3, 3] /= tag_size
                camera_to_tag[:3, 3] = [camera_to_tag[2, 3], -camera_to_tag[0, 3], camera_to_tag[1, 3]]
                # camera_to_tag[:3, 3] = [0, 0, 0]
                # print(camera_to_tag[:3, 3])

                camera_to_tag_rotation = rotations.compact_axis_angle_from_matrix(camera_to_tag[:3, :3])
                camera_to_tag_rotation = array([camera_to_tag_rotation[2], camera_to_tag_rotation[0], camera_to_tag_rotation[1]])
                camera_to_tag[:3, :3] = rotations.matrix_from_compact_axis_angle(camera_to_tag_rotation)
                # camera_to_tag[:3, :3] = rotations.matrix_from_compact_axis_angle([0, 0, 0])

                tm.add_transform(f"camera-{camera_port}", f"tag-{tag_id}", camera_to_tag)
                tm.add_transform("field", f"tag-{tag_id}", field_to_tag)
            except:
                continue

    if not tm.has_frame("field"):
        return None
    
    average_transformation = tm.get_transform("field", "robot")

    ax = tm.plot_frames_in("field", s=1)
    ax.set_xlim(-7, 7)
    ax.set_ylim(-7, 7)
    ax.set_zlim(-7, 7)
    plt.show()

    # convert the transformation to a dictionary
    return {
        "position": average_transformation[:3, 3],
        "rotation": [degrees(axis) for axis in rotations.compact_axis_angle_from_matrix(average_transformation[:3, :3])],
        "transformation": average_transformation,
        "manager": tm,
    }