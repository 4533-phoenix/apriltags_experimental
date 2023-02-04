from threading import Thread
from numpy import ndarray
from waitress import serve
from flask import Flask, Response

import cv2

class MjpegViewer:
    def __init__(self, camera_port: int, starting_port: int) -> None:
        self.mjpeg_thread = None
        self.camera_port = camera_port
        self.starting_port = starting_port
        self.frame = None

    def update_frame(self, frame: ndarray) -> None:
        self.frame = frame

    def start(self) -> None:
        self.mjpeg_thread = Thread(target=self.mjpeg_server, daemon=True, name="MJPEG Server Thread")
        self.mjpeg_thread.start()

    def mjpeg_server(self) -> None:
        app = Flask(__name__)

        @app.route("/stream.mjpeg")
        def mjpeg():
            def generate():
                while 1:
                    if self.frame is not None:
                        ret, jpeg = cv2.imencode(".jpg", self.frame)
                        if ret:
                            yield (b'--frame\r\nContent-Type: image/jpeg\r\nContent-Length: ' + str(jpeg.size).encode() + b'\r\n\r\n' + jpeg.tobytes() + b'\r\n')

            return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")
        
        @app.route("/")
        def index():
            return f"<!DOCTYPE html><html><head></head><body><h1 style='text-align: center'>Camera {self.camera_port}</h1><img src='/stream.mjpeg' width='100%'><p>URL: http://localhost:{self.starting_port + self.camera_port}/stream.mjpeg</p></body></html>"
        
        serve(app, port=(self.starting_port + self.camera_port))

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    viewer = MjpegViewer(0, 8000)
    viewer.start_mjpeg()

    while 1:
        ret, frame = cap.read()
        viewer.update_frame(frame)

        cv2.waitKey(1)