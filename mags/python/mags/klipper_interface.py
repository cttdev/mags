from enum import Enum
from threading import Lock, Thread
import time

from jsonrpcclient import Ok, Error, parse_json, request_json
from websocket import create_connection
import websocket


class Klipper():
    """
    A class to hook into the websockets interface of moonraker and send data to klipper.
    """

    def __init__(self, server_address, throw_connection_status, throw_message_status):
        self.server_address = server_address
        self.moonraker_websocket = websocket.WebSocket()
        self.connection_lock = Lock()

        self.throw_connection_status = throw_connection_status
        self.throw_message_status = throw_message_status
    
    def connect(self):
        # Try to connect to moonraker websocket
        while True:
            try:
                self.moonraker_websocket.connect("ws://" + self.server_address + "/websocket")
                self.throw_connection_status(Klipper.ConnectionStatus.CONNECTED)
                break
            except:
                self.throw_connection_status(Klipper.ConnectionStatus.DISCONNECTED)
                time.sleep(2)
                pass

    def is_connected(self):
        self.moonraker_websocket.recv()
        return self.moonraker_websocket.connected
    
    def check_klipper_connection(self):
        state = self.query("server.info")

        if state["klippy_state"] == "ready":
            self.throw_message_status(Klipper.MessageStatus.READY)
            return True
        elif state["klippy_state"] == "startup":
            time.sleep(2)
            return self.check_klipper_connection()
        else:
            self.throw_message_status(Klipper.MessageStatus.FAILURE)
            print("Klipper Is Not Ready! Status:" + self.query("printer.info")["state_message"])
            return False
    
    def query(self, request):
        # Check if connected to moonraker
        if not self.is_connected():
            self.throw_message_status(Klipper.MessageStatus.FAILURE)
            return

        # Send request to moonraker
        self.moonraker_websocket.send(request_json(request))

        # Get response from moonraker
        while True:
            response = parse_json(self.moonraker_websocket.recv())
            if isinstance(response, Ok):
                return response.result
            elif isinstance(response, Error):
                print(response.message)
                self.throw_message_status(Klipper.MessageStatus.FAILURE)


        # # Start a thread to try to connect to moonraker
        # def run():
        #     while True:
        #         # Check if connected to moonraker
        #         self.moonraker_websocket.recv()

        #         if not self.moonraker_websocket.connected:
        #             try:
        #                 self.moonraker_websocket.connect("ws://localhost:5000")
        #         self.throw_connection_status(Klipper.ConnectionStatus.CONNECTED)

    def send_initialize(self):
        # Check if connected to moonraker
        if not self.is_connected():
            self.throw_message_status(Klipper.MessageStatus.FAILURE)
            return

        # Send request to moonraker
        self.moonraker_websocket.send(request_json("printer.gcode.script", params={"script": "SET_KINEMATIC_POSITION X=20 Y=25 Z=0"}))

        # Get response from moonraker
        while True:
            try:
                response = parse_json(self.moonraker_websocket.recv())
            except KeyError:
                print("KeyError")
                continue

            if isinstance(response, Ok):
                self.throw_message_status(Klipper.MessageStatus.SUCCESS)
                return
            elif isinstance(response, Error):
                self.throw_message_status(Klipper.MessageStatus.FAILURE)
                print("Error Sending GCode: " + response.message)
                return

    def send_end(self):
        # Check if connected to moonraker
        if not self.is_connected():
            self.throw_message_status(Klipper.MessageStatus.FAILURE)
            return

        # Send request to moonraker
        self.moonraker_websocket.send(request_json("printer.gcode.script", params={"script": "M18"}))

        # Get response from moonraker
        while True:
            try:
                response = parse_json(self.moonraker_websocket.recv())
            except KeyError:
                print("KeyError")
                continue

            if isinstance(response, Ok):
                self.throw_message_status(Klipper.MessageStatus.SUCCESS)
                return
            elif isinstance(response, Error):
                self.throw_message_status(Klipper.MessageStatus.FAILURE)
                print("Error Sending GCode: " + response.message)
                return

    def send_gcode(self, gcode):
        # Check if connected to moonraker
        if not self.is_connected():
            self.throw_message_status(Klipper.MessageStatus.FAILURE)
            return

        # Send gcode to moonraker
        self.moonraker_websocket.send(request_json("printer.gcode.script", params={"script": gcode}))

        # Get response from moonraker
        while True:
            try:
                response = parse_json(self.moonraker_websocket.recv())
            except KeyError:
                print("KeyError")
                continue

            if isinstance(response, Ok):
                self.throw_message_status(Klipper.MessageStatus.SUCCESS)
                return
            elif isinstance(response, Error):
                self.throw_message_status(Klipper.MessageStatus.FAILURE)
                print("Error Sending GCode: " + response.message)
                return


    # def send_gcode(self, gcode):
        # # Check if connected to moonraker
        # if self.moonraker_websocket is None:
        #     self.throw_message_status(Klipper.MessageStatus.FAILURE)
        #     return
        # else:
        #     self.throw_message_status(Klipper.MessageStatus.SUCCESS)

        # print("here")
        # if self.moonraker_websocket:            
        #     await self.moonraker_websocket.send(request_json("ping"))
        #     response = parse_json(await self.moonraker_websocket.recv())

        #     if isinstance(response, Ok):
        #         print(response.result)

    class ConnectionStatus(Enum):
        CONNECTED = 1
        DISCONNECTED = 2

    class MessageStatus(Enum):
        SUCCESS = 1
        FAILURE = 2
        READY = 3


# klipper = Klipper("10.29.122.93:7125", lambda x: print(x), lambda x: print(x))

# klipper.connect()
# klipper.check_klipper_connection()

# klipper.send_gcode("G90")