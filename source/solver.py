from config import load_config
from pytransform3d import rotations
from pytransform3d.transform_manager import TransformManager
from numpy import array

# Load the config files
ENVIROMENT = load_config("enviroment")
CAMERAS = load_config("cameras")


def solve(data: dict[list]) -> dict:
    tm = TransformManager(strict_check=False)

    for camera_port, detections in data.items():
        camera = CAMERAS[camera_port]
        relative_camera_transform = array(camera["transformation"])

        tm.add_transform(
            "robot", f"camera-{camera_port}", relative_camera_transform)

        for tag_id, tag_transformation in detections.items():
            tag_data = ENVIROMENT["tags"][str(tag_id)]

            tag_field_transform = array(tag_data["transformation"]).reshape(4, 4)
            relative_tag_transform = tag_transformation.reshape(4, 4)

            # print (f"Tag {tag_id} relative transform: {relative_tag_transform.tolist()}")

            # swap position index 1 and 2 and invert index 2
            relative_tag_transform[1, 3], relative_tag_transform[2, 3] = relative_tag_transform[2, 3], relative_tag_transform[1, 3]
            relative_tag_transform[:3, 3] /= 1.25

            # swap rotation matrix yaw and roll
            angle = rotations.compact_axis_angle_from_matrix(relative_tag_transform[:3, :3])
            angle[1], angle[2] = angle[2], angle[1]
            relative_tag_transform[:3, :3] = rotations.matrix_from_compact_axis_angle(angle)

            position = relative_tag_transform[:3, 3]

            tm.add_transform(f"camera-{camera_port}",
                             f"tag-{tag_id}", relative_tag_transform)
            tm.add_transform(f"tag-{tag_id}", "field", tag_field_transform)

    if tm.has_frame("field"):
        estimated_bot_transform = tm.get_transform("robot", "field")
        estimated_bot_position = estimated_bot_transform[:3, 3]
        estimated_bot_rotation = estimated_bot_transform[:3, :3]

        # print(f"Estimated bot position: {estimated_bot_position}")

        return {"transformation": estimated_bot_transform, "position": estimated_bot_position, "rotation": estimated_bot_rotation, "manager": tm}
    
    return None