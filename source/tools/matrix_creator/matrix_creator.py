from pathlib import Path; from sys import path; path.append(str(Path(__file__).parent.parent.parent.resolve()))

from matrix import generate_matrix_from_values

if __name__ == "__main__":
    yaw = float(input("Yaw in degrees: "))
    pitch = float(input("Pitch in degrees: "))
    roll = float(input("Roll in degrees: "))

    forward_backward = float(input("Backward/Forward in meters: (-/+) "))
    left_right = float(input("Left/Right in meters: (-/+) "))
    up_down = float(input("Down/Up in meters: (-/+) "))

    print(generate_matrix_from_values(forward_backward, left_right, up_down, yaw, pitch, roll).tolist())