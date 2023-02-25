from functools import lru_cache
from math import sin, cos, radians, atan2, sqrt, degrees
from numpy import array, ndarray


@lru_cache(maxsize=15)
def cached_sin(x):
    return sin(x)

@lru_cache(maxsize=15)
def cached_cos(x):
    return cos(x)

def generate_matrix(yaw: float, pitch: float, roll: float) -> ndarray:
    # rotation matrix where yaw, pitch and roll are in degrees
    yaw, pitch, roll = radians(yaw), radians(pitch), radians(roll)

    R = array([
        [cached_cos(yaw) * cached_cos(pitch), cached_cos(yaw) * cached_sin(pitch) * cached_sin(roll) - cached_sin(yaw) * cached_cos(roll), cached_cos(yaw) * cached_sin(pitch) * cached_cos(roll) + cached_sin(yaw) * cached_sin(roll)],
        [cached_sin(yaw) * cached_cos(pitch), cached_sin(yaw) * cached_sin(pitch) * cached_sin(roll) + cached_cos(yaw) * cached_cos(roll), cached_sin(yaw) * cached_sin(pitch) * cached_cos(roll) - cached_cos(yaw) * cached_sin(roll)],
        [-cached_sin(pitch), cached_cos(pitch) * cached_sin(roll), cached_cos(pitch) * cached_cos(roll)]
    ])

    return R

def generate_translation(x: float, y: float, z: float) -> ndarray:
    # translation matrix
    T = array([x, y, z])

    return T

def generate_transition_from_translation_and_matrix(position: ndarray, rotation: ndarray) -> ndarray:
    # pose matrix
    matrix = array([
        [rotation[0][0], rotation[0][1], rotation[0][2], position[0]],
        [rotation[1][0], rotation[1][1], rotation[1][2], position[1]],
        [rotation[2][0], rotation[2][1], rotation[2][2], position[2]],
        [0.0, 0.0, 0.0, 1.0]
    ])

    return matrix

# generate matrix based on apriltag detection pose
def generate_matrix_from_values(x: float, y: float, z: float, yaw: float, pitch: float, roll: float) -> ndarray:
    # rotation matrix
    R = generate_matrix(yaw, pitch, roll)

    # translation matrix
    T = generate_translation(x, y, z)

    # matrix
    return generate_transition_from_translation_and_matrix(T, R)