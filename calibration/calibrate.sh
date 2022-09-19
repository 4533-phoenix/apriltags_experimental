echo "What camera is it?"
read camera

python ./calibrate.py ./cameras/"$camera"_calibration.mp4 ./cameras/"$camera"_calibration.yaml --debug-dir ./out