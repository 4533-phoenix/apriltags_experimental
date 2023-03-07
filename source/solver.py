from config import load_config
from numpy import array

# Load the config files
ENVIRONMENT = load_config("environment")
CAMERAS = load_config("cameras")

def solve(data: dict[list]) -> dict:
    transformations = []
    
    for camera_port, detections in data.items():
        camera = CAMERAS[camera_port]
        robot_to_camera = array(camera["transformation"])

        for tag_id, tag_transformation in detections.items():
            tag_data = ENVIRONMENT["tags"][str(tag_id)]
            tag_size = ENVIRONMENT["tag_size"]

            field_to_tag = array(tag_data["transformation"]).reshape(4, 4)
            camera_to_tag = array(tag_transformation).reshape(4, 4)
            camera_to_tag *= tag_size

            print(camera_to_tag[:3, 3])

    if len(transformations) == 0:
        return None 