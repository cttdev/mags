from flask_socketio import SocketIO
from flask import Flask, render_template
from matplotlib import pyplot as plt
import numpy as np
from sassutils.wsgi import SassMiddleware

import chess
from stockfish import Stockfish
from klipper_interface import Klipper
from move_manager import MoveManager
from planning.astar import Astar

from planning.board import PhysicalBoard

app = Flask(__name__, static_folder="../../static", template_folder="../../templates")
app.debug = True
app.config["TEMPLATES_AUTO_RELOAD"] = True

socketio = SocketIO(app)

# Make app use sass stylesheet
app.wsgi_app = SassMiddleware(app.wsgi_app, {
    "mags": ("../../static/sass", "../../static/css", "/static/css", False)
})

stockfish = Stockfish(path="stockfish/stockfish_15.1_linux_x64_avx2/stockfish-ubuntu-20.04-x86-64-avx2")

capture_positions = [
        np.array([400, 400]),
        np.array([400, 400]),
        np.array([400, 400]),
        np.array([400, 400]),
    ]

board = PhysicalBoard(395, 395, 22, 1, capture_positions=capture_positions)
board.reset()

astar = Astar()
astar.clear()

move_manager = MoveManager(board, astar, stockfish)

klipper = Klipper("10.29.122.93:7125", lambda x: print(x), lambda x: print(x))

klipper.connect()
klipper.check_klipper_connection()

@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("start")
def start():
    print("Starting game!")
    board.reset()
    update_state()

@socketio.on("end")
def end():
    print("Ending game!")
    board.clear()
    update_state()

@socketio.on("move")
def move(data):
    if not board.make_move(data):
        update_state()
        return
    
    print(board.get_fen())
    capture_path, path = move_manager.respond()

    if not capture_path is None:
        print(move_manager.trace_path(capture_path))
        klipper.send_gcode(move_manager.trace_path(capture_path))

    print(move_manager.trace_path(path))

    klipper.send_gcode(move_manager.trace_path(path))

    update_state()

def update_state():
    socketio.emit("update", board.get_fen())

if __name__ == "__main__":
    socketio.run(app)

    # from waitress import serve
    # serve(app, host="0.0.0.0", port=8080)