import pupil_apriltags as apriltags
import orjson as json

import pathlib
import numpy
import math
import cv2
import os

source_path = pathlib.Path(__file__).parent.resolve()
os.chdir(source_path)

with 