from flask_socketio import SocketIO
from flask import Flask, render_template
from sassutils.wsgi import SassMiddleware

import chess
from stockfish import Stockfish

app = Flask(__name__, static_folder="../static", template_folder="../templates")
app.debug = True
app.config["TEMPLATES_AUTO_RELOAD"] = True

socketio = SocketIO(app)

# Make app use sass sytlesheet
app.wsgi_app = SassMiddleware(app.wsgi_app, {
    "mags": ("../static/sass", "../static/css", "/static/css", False)
})

board = chess.Board()

stockfish = Stockfish(path="stockfish/stockfish_15.1_linux_x64_avx2/stockfish-ubuntu-20.04-x86-64-avx2")

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
    move = chess.Move.from_uci(data)

    if not board.is_legal(move):
        update_state()
        return
    else:
        board.push(chess.Move.from_uci(data))

    stockfish.set_fen_position(board.fen())

    # print(stockfish.get_board_visual())
    # print(stockfish.get_best_move())
    
    board.push(chess.Move.from_uci(stockfish.get_best_move()))

    print(board.fen())

    update_state()

def update_state():
    socketio.emit("update", board.fen())

if __name__ == "__main__":
    socketio.run(app)

    # from waitress import serve
    # serve(app, host="0.0.0.0", port=8080)