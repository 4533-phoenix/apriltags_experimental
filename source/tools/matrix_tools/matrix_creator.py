from pathlib import Path; from sys import path; path.append(str(Path(__file__).parent.parent.parent.resolve()))

from pytransform3d import rotations
from pytransform3d import transformations

if __name__ == "__main__":
    yaw = float(input("Yaw in degrees: "))
    pitch = float(input("Pitch in degrees: "))
    roll = float(input("Roll in degrees: "))

    forward_backward = float(input("Backward/Forward in meters: (-/+) "))
    left_right = float(input("Left/Right in meters: (-/+) "))
    up_down = float(input("Down/Up in meters: (-/+) "))

    print(transformations.transform_from(rotations.matrix_from_compact_axis_angle([roll, pitch, yaw]), [left_right, forward_backward, up_down]).tolist())