from config import load_config

from pytransform3d import camera
from pytransform3d import rotations
from pytransform3d import transformations
from pytransform3d.transform_manager import TransformManager

import finder
import numpy

ENVIROMENT = load_config("enviroment")
CAMERAS = load_config("cameras")

def solve(finders: list[finder.Finder]):
    # Solve position of each tag based of the camera's relative position on the robot and the environment
    for f in finders:
        camera = CAMERAS[f.camera_index]
        relative_camera_transform = numpy.array(camera["transform"])

        for tag in f.output["tags"]:
            tag_data = ENVIROMENT["tags"][str(tag.tag_id)]

            tag_field_transform = numpy.array(tag_data["transform"])
            relative_tag_transform = transformations.transform_from(tag.pose_R, tag.pose_t.flatten())