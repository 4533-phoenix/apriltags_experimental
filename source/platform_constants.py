from platform import platform
import cv2

cv2_backend = (cv2.CAP_DSHOW if platform().startswith("Windows") else cv2.CAP_V4L2)