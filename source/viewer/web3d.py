from flask_socketio import SocketIO
from threading import Thread
from pathlib import Path
from flask import Flask, abort
from flask import send_file as flask_send_file
from os.path import isfile, abspath, join, exists, isdir
from time import sleep

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

STATIC_PATH = Path(__file__).parent.resolve() / "public"
NAME = "Viewer"

transformations = {}
app = Flask(__name__)
socket = SocketIO(app, cors_allowed_origins="*")

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def send_file(path):
    path = abspath(join(STATIC_PATH, path.replace("../", "")))

    if isdir(path):
        index_path = join(path, "index.html")

        if isfile(index_path):
            path = index_path

    if not exists(path) or isdir(path):
        abort(404)

    return flask_send_file(path, mimetype=mimetypes.get(Path(path).suffix, "text/plain"))

def socket_handler(delay=0.1):
    while 1:
        socket.emit("transformations", transformations)
        sleep(delay)

def start(host="", port=8000):
    print(f"Starting {NAME} on http://localhost:{port}")
    socket.start_background_task(target=socket_handler)
    socket.run(app, host, port)

def thread_start(host="", port=8000):
    Thread(target=start, args=(host, port), daemon=True).start()