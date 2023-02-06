from enum import Enum
from threading import Event
import threading
import gpiozero
import numpy as np

OUTPUT_PINS = [1, 2, 3, 4, 5, 6, 7, 8]
INPUT_PINS = [9, 10, 11, 12, 13, 14, 15, 16]

MOVE_TIME_THRESHOLD = 0.5 # Seconds

class MoveObserver:
    """
    Observes the current state of the board and detects moves.
    
    Uses BCS:
    Board Coordinate System: BCS -> [0, 8]:[0, 8]
    [0, 7]
    y
    ^
    |
    |
    0,0 -----> x [7, 0]

    Uses a 8x8 binary board to store the state of the board.
    1 -> Piece is present
    0 -> Piece is not present

    Real Board: The reed switch array
    Binary Board: The 8x8 binary board
    Board(PhysicalBoard): The internal stored chessboard representation
    """

    def __init__(self, board, throw_observation_status):
        self.board = board
        self.throw_observation_status = throw_observation_status

        self.binary_board = np.zeros((8, 8), dtype=np.int8)

        self.output_pins = [gpiozero.DigitalOutputDevice(pin) for pin in OUTPUT_PINS]
        self.input_pins = [gpiozero.DigitalInputDevice(pin, pull_up=False) for pin in INPUT_PINS]


    def reset(self):
        """"
        Resets the board to the starting position.

        """
        # Set all the outputs to low
        for pin in self.output_pins:
            pin.off()

    def sample_board(self):
        """
        Samples the current state of the board and updates the binary board.

        """
        for i in range(len(self.output_pins)):
            # Set the output pin of the column to high
            self.output_pins[i].on()

            for j in range(len(self.input_pins)):
                # Read the input pin of the row
                if self.input_pins[j].value:
                    self.binary_board[j, i] = 1 # Piece is present at column i, row j -> (j, i) in BCS

            self.output_pins[i].off()

    def check_board_state(self, other_binary_board):
        """
        Checks if the other board state is the same as the internally stored board.

        """

        if np.array_equal(self.binary_board, other_binary_board):
            return True
        else:
            return False

    def verify_board_state(self):
        # Sample the real board state
        self.sample_board()

        # Check if the real board state is the same as the internally stored board
        if self.check_board_state(self.board.get_binary_board()):
            self.throw_observation_status(self.ObservationStatus.BOARD_MATCH_ERROR)

    def extract_move(self, previous_binary_board):
        """
        Extracts the move made on the board.

        """
        # Find the difference between the previous board state and the current board state
        difference = self.binary_board - previous_binary_board

        # When we subtract the two boards the start of the move will be when the board goes from 0 -> 1 (1 - 0 = 1) and the end of the move will be when the board goes from 1 -> 0 (0 - 1 = -1)
        move_start = np.argwhere(difference == 1)
        move_end = np.argwhere(difference == -1)

        # Convert the move coordinates to CCS
        move_start_ccs = self.board.bcs_2_ccs(move_start)
        move_end_ccs = self.board.bcs_2_ccs(move_end)

        # Return the move
        return move_start_ccs + move_end_ccs

    def detect_move(self):
        """
        Detects a move on the board.

        NOTE: THIS IS A BLOCKING CALL!

        """
        stored_binary_board = self.board.get_binary_board()

        # Wait until a move is detected
        while True:
            self.sample_board()

            # Check if the real board state is the same as the internally stored board
            if not self.check_board_state(stored_binary_board):
                # If the board state is different, a move has started, so break out of the loop
                previous_binary_board = self.binary_board
                break
                
        # Setup the timer threading
        time_out_condition = Event()
        time_out_timer = threading.Timer(MOVE_TIME_THRESHOLD, time_out_condition.set)  

        # Start the timer
        time_out_timer.start()

        # To detect the end of a move we constantly compare the current board state to the previous board state and once they
        # are the same for a specified settling time, we can assume that the move has ended
        while not time_out_condition.is_set():
            self.sample_board()

            # Check if the real board state is the same as the previous board state
            if not self.check_board_state(previous_binary_board):
                # If the board state isn't the same as the previous board state, a move is still being made, so reset the timer
                time_out_timer.cancel()
                time_out_timer.start()

                # Update the previous board state
                previous_binary_board = self.binary_board

        # Once we exit the loop, we are sure a move has ended
        # Extract the move by looking at the difference between the stored board state and the current board state
        return self.extract_move(stored_binary_board)

    class ObservationStatus(Enum):
        BOARD_MATCH_ERROR = 1
        MOVE_MADE = 2