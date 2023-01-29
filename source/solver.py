from config import load_config
from pytransform3d import transformations
from pytransform3d.transform_manager import TransformManager
from numpy import array
from finder import Finder

# Load the config files
ENVIROMENT = load_config("enviroment")
CAMERAS = load_config("cameras")


def solve(solver_inputs: list[dict]) -> TransformManager:
    """Solve for the position of the robot."""

    tm = TransformManager(strict_check=False)

    for solver_input in solver_inputs:
        camera_index = solver_input["camera_index"]
        camera = CAMERAS[camera_index]
        relative_camera_transform = array(camera["transform"])

        tm.add_transform(
            "robot", f"camera-{camera_index}", relative_camera_transform)

        for tag in solver_input["output"]["tags"]:
            tag_data = ENVIROMENT["tags"][str(tag.tag_id)]

            tag_field_transform = array(tag_data["transform"]).reshape(4, 4)

            relative_tag_transform = transformations.transform_from(
                tag.pose_R, tag.pose_t.flatten() / 1.25)

            tm.add_transform(f"camera-{camera_index}",
                             f"tag-{tag.tag_id}", relative_tag_transform)
            tm.add_transform(f"tag-{tag.tag_id}", "field", tag_field_transform)

            print(relative_tag_transform[:3, 3][2])

    # return tm

    tm.write_png("output.png")

    return tm