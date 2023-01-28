from pytransform3d import transformations
from pytransform3d import rotations

import flask_socketio
import threading
import pathlib
import flask
import numpy
import os

mimetypes = {
    ".css": "text/css",
    ".js": "text/javascript",
    ".html": "text/html",
    ".htm": "text/html",
    ".txt": "text/plain",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".svgz": "image/svg+xml",
    ".json": "application/json",
}

STATIC_PATH = pathlib.Path(__file__).parent.resolve() / "public"
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = os.environ.get("PORT", 8000)
NAME = "Viewer"

tm = None
app = flask.Flask(__name__)
socket = flask_socketio.SocketIO(app, cors_allowed_origins="*")

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def send_file(path):
    path = os.path.abspath(os.path.join(STATIC_PATH, path.replace("../", "")))

    if os.path.isdir(path):
        index_path = os.path.join(path, "index.html")

        if os.path.isfile(index_path):
            path = index_path

    if not os.path.exists(path) or os.path.isdir(path):
        flask.abort(404)

    return flask.send_file(path, mimetype=mimetypes.get(os.path.splitext(path)[1], "text/plain"))

def socket_handler(delay=0.1):
    while True:
        cur_tm = tm
        if cur_tm and cur_tm.has_frame("field"):
            robot_transform_matrix = numpy.array(cur_tm.get_transform("field", "robot"))

            socket.emit("transformations", {
                "robot": {
                    "matrix": robot_transform_matrix.flatten().tolist(),
                }
            })
        socket.sleep(delay)

def start(host=HOST, port=PORT):
    print(f"Starting {NAME} on http://localhost:{port}")
    socket.start_background_task(target=socket_handler, delay=0.1)
    socket.run(app, host, port)

def thread_start(host=HOST, port=PORT):
    threading.Thread(target=start, args=(host, port), daemon=True).start()