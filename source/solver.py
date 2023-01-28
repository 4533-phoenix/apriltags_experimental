from config import load_config

from pytransform3d import transformations
from pytransform3d.transform_manager import TransformManager

import finder
import numpy

ENVIROMENT = load_config("enviroment")
CAMERAS = load_config("cameras")

def solve(finders: list[finder.Finder]):
    tm = TransformManager(strict_check=False)

    for f in finders:
        camera = CAMERAS[f.camera_index]
        relative_camera_transform = numpy.array(camera["transform"])

        tm.add_transform("robot", f"camera-{f.camera_index}", relative_camera_transform)

        for tag in f.output["tags"]:
            tag_data = ENVIROMENT["tags"][str(tag.tag_id)]

            tag_field_transform = numpy.array(tag_data["transform"]).reshape(4, 4)

            relative_tag_transform = transformations.transform_from(tag.pose_R, tag.pose_t.flatten() / 1.25)

            tm.add_transform(f"camera-{f.camera_index}", f"tag-{tag.tag_id}", relative_tag_transform)
            tm.add_transform(f"tag-{tag.tag_id}", "field", tag_field_transform)

            print(relative_tag_transform[:3, 3][2])

    if tm.has_frame("field"):
        robot_transform = tm.get_transform("field", "robot")
        
    else:
        pass
        # print("No tag found")

    return tm
    
    tm.write_png("output.png")