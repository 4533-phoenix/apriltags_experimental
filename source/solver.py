from config import load_config
from pytransform3d import transformations
from pytransform3d import rotations
from numpy import matmul, mean, array
from math import degrees

# Load the config files
ENVIROMENT = load_config("enviroment")
CAMERAS = load_config("cameras")


def solve(data: dict[dict]) -> dict:
    """Solve for the position of the robot.
    input is a dict of dicts of camera ids connected to a dict with validity, detections, and status
    detections is a list of pupil apriltag detection objects
    returns a dicts with position and heading"""

    estimated_bot_transforms = []
    for camera_id, data in data.items():
        for tag in data["detections"]:
            camera_to_tag_transform = transformations.transform_from(tag.pose_R, tag.pose_t.flatten() / 1.25)
            tag_to_camera_transform = transformations.invert_transform(camera_to_tag_transform, strict_check=False, check=False)

            # print(camera_to_tag_transform)
            # print(tag_to_camera_transform)

            robot_to_camera_transform = array(CAMERAS[camera_id]["transformation"]).reshape(4, 4)
            camera_to_robot_transform = transformations.invert_transform(robot_to_camera_transform, strict_check=False, check=False)

            # print(robot_to_camera_transform)
            # print(camera_to_robot_transform)

            field_to_tag_transform = array(ENVIROMENT["tags"][str(tag.tag_id)]["transformation"]).reshape(4, 4)

            # print(field_to_tag_transform)

            field_to_camera_transform = matmul(field_to_tag_transform, tag_to_camera_transform)
            field_to_robot_transform = matmul(field_to_camera_transform, camera_to_robot_transform)

            estimated_bot_transforms.append(field_to_robot_transform)

    if len(estimated_bot_transforms) > 0:
        # average all transforms together
        estimated_bot_transform = mean(estimated_bot_transforms, axis=0)
        estimated_bot_position = estimated_bot_transform[:3, 3]
        estimated_bot_rotation = estimated_bot_transform[:3, :3]
        # estimated_bot_heading = degrees(rotations.axis_angle_from_matrix(estimated_bot_rotation, strict_check=False, check=False)[0])

        return {"transformation": estimated_bot_transform, "position": estimated_bot_position, "rotation": estimated_bot_rotation}