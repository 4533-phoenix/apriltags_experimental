from pytransform3d.transform_manager import TransformManager
import matplotlib.pyplot as plt
import pupil_apriltags as apriltag
import solver
import numpy

solver.ENVIROMENT = {
    "tags": {
        "0": {
            "transformation": [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ]
        }
    }
}

# confiure solve cameras to be the same as the test data
solver.CAMERAS = {
    "0": {
        "transformation": [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ]
    }
}


def test_solve(testing_entry: dict):
    """Test the solve function

    Args:
        testing_entry (dict): The test data
    """
    # get the test data
    enviroment = testing_entry["enviroment"]
    cameras = testing_entry["cameras"]
    detected = testing_entry["detected"]
    expected = testing_entry["expected"]

    #  convert all the detected tags to apriltag detections
    new_detected = {}
    for camera_id, camera in detected.items():
        for tag in camera:
            apriltag_detection = apriltag.Detection()
            apriltag_detection.tag_id = tag["tag_id"]
            apriltag_detection.pose_R = numpy.array(tag["pose_R"])
            apriltag_detection.pose_t = numpy.array(tag["pose_t"])

            if camera_id not in new_detected:
                new_detected[camera_id] = []
            new_detected[camera_id].append(apriltag_detection)

    detected = new_detected
    del new_detected

    # set the enviroment and cameras
    solver.ENVIROMENT = enviroment
    solver.CAMERAS = cameras

    # run the solve function
    result = solver.solve(detected)

    if result is None:
        print("None")
        return
    
    # convert to result: flip z
    # result["position"][2] = -result["position"][2]
    # result["position"] = numpy.flip(result["position"], 0)

    print(result["position"])

    # check the result
    print(numpy.allclose(result["rotation"], expected["rotation"], atol=0.01))
    print(numpy.allclose(result["position"], expected["position"], atol=0.01))

    # # plot the result
    # tm = result["manager"]
    # tm.plot_frames_in("field", s=0.1)
    # plt.show()

# run the test
testing_data = [
    {
        "enviroment": {
            "tags": {
                "0": {
                    "transformation": [
                        [1.0, 0.0, 0.0, 0.0],
                        [0.0, 1.0, 0.0, 0.0],
                        [0.0, 0.0, 1.0, 0.0],
                        [0.0, 0.0, 0.0, 1.0],
                    ]
                }
            }
        },
        "cameras": {
            "0": {
                "transformation": [
                    [1.0, 0.0, 0.0, 0.0],
                    [0.0, 1.0, 0.0, 0.0],
                    [0.0, 0.0, 1.0, 0.0],
                    [0.0, 0.0, 0.0, 1.0],
                ],
            }
        },
        "detected": {
            "0": [
                {
                    "tag_id": 0,
                    "pose_R": [
                        [1.0, 0.0, 0.0],
                        [0.0, 1.0, 0.0],
                        [0.0, 0.0, 1.0],
                    ],
                    "pose_t": [0.0, 0.0, 0.0]
                }
            ]
        },
        "expected": {
            "position": [0.0, 0.0, 0.0],
            "rotation": [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
            ]
        }
    },
    {
        "enviroment": {
            "tags": {
                "0": {
                    "transformation": [
                        # 0.5 meters backwards (z), 0 meters to the left(x), 0 meters up(y), 0 degrees rotation
                        [1.0, 0.0, 0.0, 0.0],
                        [0.0, 1.0, 0.0, 0.0],
                        [0.0, 0.0, 1.0, -0.5],
                        [0.0, 0.0, 0.0, 1.0]
                    ]
                }
            }
        },
        "cameras": {
            "0": {
                "transformation": [
                    # 0.5 meters forward (z), 0 meters to the left(x), 0 meters up(y), 0 degrees rotation
                    [1.0, 0.0, 0.0, 0.0],
                    [0.0, 1.0, 0.0, 0.0],
                    [0.0, 0.0, 1.0, 0.5],
                    [0.0, 0.0, 0.0, 1.0]
                ],
            }
        },
        "detected": {
            "0": [
                {
                    "tag_id": 0,
                    "pose_R": [
                        [1.0, 0.0, 0.0],
                        [0.0, 1.0, 0.0],
                        [0.0, 0.0, 1.0],
                    ],
                    "pose_t": [0.0, 0.0, 1.0] # 0 meter to the left (x), 0 meters up (y), 1 meters forward (z)
                }
            ]
        },
        "expected": {
            # 1 meters backwards (z), 0 meters to the left(x), 0 meters up(y), 0 degrees rotation
            "position": [0.0, 0.0, 1.0],
            "rotation": [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
            ]
        }
    },
    {
        "enviroment": {
            "tags": {
                "0": {
                    "transformation": [
                        # 0.5 meters backwards (z), 0 meters to the left(x), 0 meters up(y), 0 degrees rotation
                        [1.0, 0.0, 0.0, 0.0],
                        [0.0, 1.0, 0.0, 0.0],
                        [0.0, 0.0, 1.0, -0.5],
                        [0.0, 0.0, 0.0, 1.0]
                    ]
                }
            }
        },
        "cameras": {
            "0": {
                "transformation": [
                    # 0.5 meters forward (z), 0 meters to the left(x), 0 meters up(y), 0 degrees rotation
                    [1.0, 0.0, 0.0, 0.0],
                    [0.0, 1.0, 0.0, 0.0],
                    [0.0, 0.0, 1.0, 0.5],
                    [0.0, 0.0, 0.0, 1.0]
                ],
            }
        },
        "detected": {
            "0": [
                {
                    "tag_id": 0,
                    "pose_R": [
                        [1.0, 0.0, 0.0],
                        [0.0, 1.0, 0.0],
                        [0.0, 0.0, 1.0],
                    ],
                     # 1 meter to the left (x), 0 meters up (y), 1 meters forward (z)
                    "pose_t": [-1.0, 0.0, 1.0]
                }
            ]
        },
        "expected": {
            # 1 meters backwards (z), 1 meters to the left(x), 0 meters up(y), 0 degrees rotation
            "position": [-1.0, 0.0, 1.0],
            "rotation": [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
            ]
        }
    },
    {
        "enviroment": {
            "tags": {
                "0": {
                    "transformation": [
                        # 0.5 meters backwards (z), 0 meters to the left(x), 0 meters up(y), 0 degrees rotation
                        [1.0, 0.0, 0.0, 0.0],
                        [0.0, 1.0, 0.0, 0.0],
                        [0.0, 0.0, 1.0, -0.5],
                        [0.0, 0.0, 0.0, 1.0]
                    ]
                }
            }
        },
        "cameras": {
            "0": {
                "transformation": [
                    # 0.5 meters forward (z), 0 meters to the left(x), 0 meters up(y), 0 degrees rotation
                    [1.0, 0.0, 0.0, 0.0],
                    [0.0, 1.0, 0.0, 0.0],
                    [0.0, 0.0, 1.0, 0.5],
                    [0.0, 0.0, 0.0, 1.0]
                ],
            }
        },
        "detected": {
            "0": [
                {
                    "tag_id": 0,
                    "pose_R": [
                        [1.0, 0.0, 0.0],
                        [0.0, 1.0, 0.0],
                        [0.0, 0.0, 1.0],
                    ],
                    # 1 meter to the left (x), 1 meters up (y), 1 meters forward (z)
                    "pose_t": [-1.0, 1.0, 1.0]
                }
            ]
        },
        "expected": {
            # 1 meters backwards (z), 1 meters to the left(x), 1 meters up(y), 0 degrees rotation
            "position": [-1.0, 1.0, 1.0],
            "rotation": [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
            ]
        }
    },
]

for testing_entry in testing_data:
    test_solve(testing_entry)