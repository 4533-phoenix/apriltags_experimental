from pathlib import Path; from sys import path; path.append(str(Path(__file__).parent.parent.parent.resolve()))

from config import save_config
from numpy import zeros, prod, indices, float32
from argparse import ArgumentParser
from platform_constants import cv2_backend

import cv2


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Calibrate camera using a video of a chessboard or a sequence of images.")
    parser.add_argument("input", help="Input camera port")
    parser.add_argument("out", help="Output name of calibration json file")
    parser.add_argument(
        "--square_size", help="Size of a chessboard square", default=1.0)
    parser.add_argument(
        "--pattern_size", help="Size of a chessboard pattern", default="9x6")
    parser.add_argument("--camera_resolution",
                        help="Camera resolution", default="640x480")
    parser.add_argument("--frames_per_second",
                        help="Camera frames per second", type=int, default=30)

    args = parser.parse_args()

    capture = cv2.VideoCapture(int(args.input), cv2_backend)
    if not capture.isOpened():
        raise RuntimeError(f"Failed to open camera {args.input}")

    pattern_size = tuple(map(int, args.pattern_size.split("x")))
    camera_resolution = tuple(map(int, args.camera_resolution.split("x")))

    capture.set(cv2.CAP_PROP_FRAME_WIDTH, camera_resolution[0])
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_resolution[1])
    capture.set(cv2.CAP_PROP_FPS, args.frames_per_second)

    pattern_points = zeros((prod(pattern_size), 3), float32)
    pattern_points[:, :2] = indices(pattern_size).T.reshape(-1, 2)
    pattern_points *= float(args.square_size)

    obj_points = []
    img_points = []

    while 1:
        try:
            ret, frame = capture.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            found, corners = cv2.findChessboardCorners(gray, pattern_size)

            if found:
                cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1),
                                 (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1))
                cv2.drawChessboardCorners(frame, pattern_size, corners, found)

                obj_points.append(pattern_points)
                img_points.append(corners.reshape(-1, 2))

            cv2.imshow("Calibration", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        except KeyboardInterrupt:
            break

    capture.release()
    cv2.destroyAllWindows()

    additional_config = {
        "detector": {
            "nthreads": 4,
            "quad_decimate": 1.0,
            "quad_sigma": 0.0,
            "refine_edges": 1,
            "decode_sharpening": 0.25
        }
    }

    if not obj_points:
        raise RuntimeError("No chessboard found")

    def recursive_config_asker(config: dict) -> None:
        for key, value in config.items():
            if isinstance(value, dict):
                recursive_config_asker(value)
            else:
                config[key] = input(f"{key} [{value}]: ") or value

    recursive_config_asker(additional_config)

    print("Generating calibration. This may take a while...")
    rms, camera_matrix, dist_coefs, rvecs, tvecs = cv2.calibrateCamera(
        obj_points, img_points, camera_resolution, None, None, flags=cv2.CALIB_USE_LU | cv2.CALIB_CB_FAST_CHECK)

    print("Saving calibration...")
    calibration = {"rms": rms, "camera_matrix": camera_matrix.tolist(
    ), "dist_coefs": dist_coefs.flatten().tolist(), **additional_config}
    save_config("calibrations/" + args.out, calibration)
