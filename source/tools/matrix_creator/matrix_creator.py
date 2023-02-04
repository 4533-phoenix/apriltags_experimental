from pytransform3d import transformations
from pytransform3d import rotations
from numpy import array, hstack, around
from math import radians

if __name__ == "__main__":
    # 3 rotations
    yaw = radians(float(input("Yaw in degrees: ")))
    pitch = radians(float(input("Pitch in degrees: ")))
    roll = radians(float(input("Roll in degrees: ")))

    forward_backward = float(input("Backward/Forward in meters: (-/+) "))
    left_right = float(input("Left/Right in meters: (-/+) "))
    up_down = float(input("Down/Up in meters: (-/+) "))

    transformation = around(transformations.transform_from_pq(
        hstack(
            (
                array([forward_backward, up_down, left_right]),
                rotations.quaternion_from_extrinsic_euler_xyz(array([roll, yaw, pitch]))
            )
        )
    ), 9)

    print(transformation.tolist())