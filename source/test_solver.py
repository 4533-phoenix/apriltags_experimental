import matplotlib.pyplot as plt
import solver
import numpy


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
        new_detected[camera_id] = {}

        for tag in camera:
            new_detected[camera_id][tag["tag_id"]] = tag["transformation"]

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

    # print the result
    print(
        f"Rounded position: {numpy.around(result['position'])}, Position: {result['position']}, Decimal position: {numpy.around(result['position'], decimals=10)}")

# run the test
testing_data = [
    {
        "enviroment": {
            "tags": {
                "0": {
                    "transformation": matrix.generate_matrix_from_values(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
                }
            }
        },
        "cameras": {
            "0": {
                "transformation": matrix.generate_matrix_from_values(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
            }
        },
        "detected": {
            "0": [
                {
                    "tag_id": 0,
                    "transformation": matrix.generate_matrix_from_values(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
                }
            ]
        },
        "expected": {
            "transformation": matrix.generate_matrix_from_values(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        }
    },
    {
        "enviroment": {
            "tags": {
                "0": {
                    "transformation": matrix.generate_matrix_from_values(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
                }
            }
        },
        "cameras": {
            "0": {
                "transformation": matrix.generate_matrix_from_values(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
            }
        },
        "detected": {
            "0": [
                {
                    "tag_id": 0,
                    "transformation": numpy.array([[0.9968423625549117, 0.07138991411417328, 0.0347675765435801, 0.07324227659190707], [-0.07350673767469834, 0.9952401647920434, 0.0639826062389595, 0.09028933904083317], [-0.030034375844452347, -0.06633622349423896, 0.9973451968702495, 1.0699796460627256], [0.0, 0.0, 0.0, 1.0]])
                }
            ]
        },
        "expected": {
            "transformation": matrix.generate_matrix_from_values(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        }
    },
    {
        "enviroment": {
            "tags": {
                "0": {
                    "transformation": matrix.generate_matrix_from_values(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
                }
            }
        },
        "cameras": {
            "0": {
                "transformation": matrix.generate_matrix_from_values(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
            }
        },
        "detected": {
            "0": [
                {
                    "tag_id": 0,
                    "transformation": numpy.array([[0.998801160088786, 0.014063314472334776, 0.04688780002673772, 0.08959080408959097], [-0.015222875040768358, 0.9995847566059315, 0.024465862677509467, -0.002412789322832038], [-0.046524259056843424, -0.025150299145612953, 0.9986004985839422, 0.9918688281231794], [0.0, 0.0, 0.0, 1.0]])
                }
            ]
        },
        "expected": {
            "transformation": matrix.generate_matrix_from_values(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        }
    }
]

for testing_entry in testing_data:
    test_solve(testing_entry)

# while True:
#     x = float(input("x: "))
#     y = float(input("y: "))
#     z = float(input("z: "))
#     yaw = float(input("yaw: "))
#     pitch = float(input("pitch: "))
#     roll = float(input("roll: "))
#     print(matrix.generate_matrix_from_pose(x, y, z, yaw, pitch, roll))
