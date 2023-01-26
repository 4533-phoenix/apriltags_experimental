from pytransform3d import transformations
from pytransform3d import rotations

import numpy

if __name__ == "__main__":
    # 3 rotations
    yaw = float(input("Yaw in degrees: ")) / 360
    pitch = float(input("Pitch in degrees: ")) / 360
    roll = float(input("Roll in degrees: ")) / 360

    forward_backward = float(input("Backward/Forward in meters: (-/+) "))
    left_right = float(input("Left/Right in meters: (-/+) "))
    up_down = float(input("Down/Up in meters: (-/+) "))

    transformation = transformations.transform_from_pq(
        numpy.hstack(
            (
                numpy.array([forward_backward, left_right, up_down]),
                rotations.quaternion_from_extrinsic_euler_xyz(numpy.array([yaw, pitch, roll]))
            )
        )
    )

    print(transformation)