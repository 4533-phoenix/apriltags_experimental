import numpy as np
import matplotlib.pyplot as plt
from pytransform3d import rotations as pr
from pytransform3d import transformations as pt
from pytransform3d.transform_manager import TransformManager
from math import pi

origin_to_tag_1 = np.array([[-1.0, 0.0, 0.0, 7.2431], [0.0, -1.0, 0.0, -2.93659], [0.0, 0.0, 1.0, 0.46272], [0.0, 0.0, 0.0, 1.0]])
origin_to_tag_8 = np.array([[1.0, 0.0, 0.0, -7.2431], [0.0, 1.0, 0.0, -2.93659], [0.0, 0.0, 1.0, 0.46272], [0.0, 0.0, 0.0, 1.0]])

tag_1_to_camera_1 = pt.transform_from(pr.matrix_from_compact_axis_angle([0, 0, 0]), [0, 1, 0])
tag_8_to_camera_2 = pt.transform_from(pr.matrix_from_compact_axis_angle([0, 0, 0]), [0, 1, 0])

tm = TransformManager()
tm.add_transform("origin", "tag_1", origin_to_tag_1)
tm.add_transform("origin", "tag_8", origin_to_tag_8)

tm.add_transform("tag_1", "camera_1", tag_1_to_camera_1)
tm.add_transform("tag_8", "camera_2", tag_8_to_camera_2)

ax = tm.plot_frames_in("origin", s=0.1)
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.set_zlim(-1, 1)
plt.show()