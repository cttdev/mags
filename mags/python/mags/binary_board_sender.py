import json
import logging
from threading import Thread
import time
import numpy as np
from websocket_server import WebsocketServer

from move_observer import MoveObserver
from planning.board import PhysicalBoard

# move_observer = MoveObserver(PhysicalBoard(395, 395, 22, 1), lambda x: print(x))

binary_board_state = np.zeros((8, 8), dtype=np.int8).tolist()

server = WebsocketServer(host='localhost', port=5001, loglevel=logging.INFO)

websocket_thread = Thread(target=server.serve_forever)
websocket_thread.deamon = True
websocket_thread.start()

while True:
    message = json.dumps(binary_board_state)
    server.send_message_to_all(message)
    print(message)
    time.sleep(0.1)
