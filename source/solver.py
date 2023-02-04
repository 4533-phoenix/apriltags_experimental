from config import load_config
from pytransform3d import transformations
from pytransform3d.transform_manager import TransformManager
from numpy import matmul, mean, array
from math import degrees

# Load the config files
ENVIROMENT = load_config("enviroment")
CAMERAS = load_config("cameras")


def solve(data: dict[dict]) -> dict:
    tm = TransformManager(strict_check=False)

    for camera_port, data in data.items():
        camera = CAMERAS[camera_port]
        relative_camera_transform = array(camera["transformation"])

        tm.add_transform(
            "robot", f"camera-{camera_port}", relative_camera_transform)

        for tag in data["detections"]:
            tag_data = ENVIROMENT["tags"][str(tag.tag_id)]

            tag_field_transform = array(tag_data["transformation"]).reshape(4, 4)

            relative_tag_transform = transformations.transform_from(
                tag.pose_R, tag.pose_t.flatten() / 1.25)

            tm.add_transform(f"camera-{camera_port}",
                             f"tag-{tag.tag_id}", relative_tag_transform)
            tm.add_transform(f"tag-{tag.tag_id}", "field", tag_field_transform)

    if tm.has_frame("field"):
        estimated_bot_transform = tm.get_transform("field", "robot")
        estimated_bot_position = estimated_bot_transform[:3, 3]
        estimated_bot_rotation = estimated_bot_transform[:3, :3]

        # print(f"Estimated bot position: {estimated_bot_position}")

        return {"transformation": estimated_bot_transform, "position": estimated_bot_position, "rotation": estimated_bot_rotation}