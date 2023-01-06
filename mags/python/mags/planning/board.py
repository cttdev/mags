import string
import chess
import chess.svg
import cairosvg
from matplotlib import pyplot as plt
from PIL import Image
import io
import numpy as np

from .graph import Circle, Graph


class PhysicalBoard():
    """
    A class to represent a chess board for move making.
    NOTE: All dimensions are in mm.

    Board Coordinate System: BCS -> [0, 7]:[0, 7]
    Chess Coordinate System: CCS -> [a, h]:[1, 8]
    [0, 7] (a, 8)
    y
    ^
    |
    |
    0,0 -----> x [7, 0] (h, 1)
    """

    def __init__(self, length, width, piece_diameter, clearance, capture_positions):
        self.board = chess.Board()

        # Store the board dimensions and piece diameter
        self.length = length
        self.width = width

        self.piece_diameter = piece_diameter

        # Initialize the capture positions
        self.capture_positions = capture_positions
        self.open_capture_positions = capture_positions.copy()

        # Calculate the piece clearance radius
        # This is the raidus of the circle around the piece used for path finding
        piece_radius = piece_diameter / 2.0
        self.clearance_radius = piece_radius * 2 + clearance

        # Square mapping
        # The mapping from the board coordinate system to the square positions the square positions are stored in a numpy array with their BCS index 
        # and a dictionary is used to map their CCS index to their BCS index
        
        # Generate a numpy array with the positions of all the squares
        self.square_positions = np.zeros((8, 8, 2))
        self.square_indices = {}

        square_width = width / 8.0
        square_length = length / 8.0

        # Generate the x positions
        x_positions = np.arange(square_width / 2.0, width, square_width)

        # Generate the y positions
        y_positions = np.arange(square_length / 2.0, length, square_length)

        # Put them in the square positions array
        for i in range(8):
            for j in range(8):
                # Put the x and y positions in the square positions array
                self.square_positions[i, j, 0] = x_positions[i]
                self.square_positions[i, j, 1] = y_positions[j]
                
                # Put the CCS to BCS mapping in the square indices dictionary
                self.square_indices[string.ascii_lowercase[i] + str(j + 1)] = (i, j)

    def get_fen(self):
        """
        Get the FEN representation of the board.
        """
        return self.board.fen()

    def get_piece_diameter(self):
        """
        Get the piece diameter.
        """
        return self.piece_diameter

    def reset(self, fen=None):
        """
        Reset and clear the board.
        """
        self.open_capture_positions = self.capture_positions.copy()

        if fen is not None:
            self.board.set_fen(fen)
        else:
            self.board.reset()
    
    def clear(self):
        """
        Clear the board.
        """
        self.open_capture_positions = self.capture_positions.copy()

        self.board.clear()

    def check_capture(self, move):
        """
        Check if a move is a capture.
        """
        move = chess.Move.from_uci(move)

        return self.board.is_capture(move)

    def get_open_capture_position(self):
        """
        Get the first open capture position.
        """
        # Check if there are any open capture positions
        try:
            return self.open_capture_positions.pop(0)
        # If there are no open capture positions return the first capture position
        except IndexError:
            return self.capture_positions[0]

    def make_move(self, move):
        """
        Check's if a move is legal and then makes it.
        NOTE: This function updates the board's state
        """
        move = chess.Move.from_uci(move)

        # Check if the move is legal or not
        if self.board.is_legal(move):
            self.board.push(move)
        else:
            return

    def get_square_position(self, square):
        """
        Get the position of a UCI square on the board.
        """
        # Get the square index
        square_index = self.square_indices[square]

        # Get the square position
        square_position = self.square_positions[square_index[0], square_index[1], :]

        return square_position

    def generate_map(self, excluded_squares=[]):
        """
        Generate a map of the board.
        Exclude the squares in the excluded_squares list.
        """
        # Get the board map from python chess
        piece_map = self.board.piece_map()

        # Create a list to store the board map
        board_map = []

        # Generate the excluded squares indices in BCS
        excluded_squares_indices = []
        for square in excluded_squares:
            excluded_squares_indices.append(self.square_indices[square])
        
        # Loop through the board map
        for position, _ in piece_map.items():
            # Piece map is labeled with a row-major index
            #
            # 56 57 58 59 60 61 62 63
            # ...
            # 0  1  2  3  4  5  6  7

            # Get x and y position of the piece on the board
            board_index = np.unravel_index(position, (8, 8)) #  Returns a tuple of (row, col)

            # We need to reverse the unraveled index to get the BCS index
            # row = y
            # col = x
            board_index = (board_index[1], board_index[0])

            if board_index in excluded_squares_indices:
                continue
            
            # Get the x and y position of the piece on the board
            x = self.square_positions[board_index[0], board_index[1], 0]
            y = self.square_positions[board_index[0], board_index[1], 1]

            # Add the piece circle to the board map
            board_map.append(Circle(self.clearance_radius, np.array([x, y])))

        # Create a graph from the board map
        return Graph(board_map)

    def plot_background(self, ax):
        """
        Plots the background of the board.
        
        """

        # Render chess board svg
        svg = chess.svg.board(
            board = self.board,
            coordinates = False
        )

        # Convert svg to png
        png = cairosvg.svg2png(svg, dpi=100)

        # Plot the png
        img = Image.open(io.BytesIO(png))
        ax.imshow(img, extent=[0, self.width, 0, self.length])

    def plot_board(self, ax):
        """
        Plots the pieces on the board.
    
        """

        # Get the board map from python chess
        piece_map = self.board.piece_map()

        # Loop through the board map
        for position, _ in piece_map.items():
            # Piece map is labeled with a row-major index
            #
            # 56 57 58 59 60 61 62 63
            # ...
            # 0  1  2  3  4  5  6  7

            # Get x and y position of the piece on the board
            board_index = np.unravel_index(position, (8, 8)) # Returns a tuple of (row, col)

            # We need to reverse the unraveled index to get the BCS index
            # row = y
            # col = x
            board_index = (board_index[1], board_index[0])
            
            # Get the x and y position of the piece on the board
            x = self.square_positions[board_index[0], board_index[1], 0]
            y = self.square_positions[board_index[0], board_index[1], 1]

            # Plot a circle at the position of the piece
            ax.add_patch(plt.Circle([x, y], self.piece_diameter / 2, fill=False, color="green"))

if __name__ == "__main__":
    capture_positions = [
        np.array([450, 450]),
        np.array([450, 400]),
        np.array([450, 350]),
        np.array([450, 300]),
    ]

    board = PhysicalBoard(400, 400, 10, 3, capture_positions)
    # board.reset("r1b1k1nr/p2p1pNp/n2B4/1p1NP2P/6P1/3P1Q2/P1P1K3/q5b1")
    board.reset()

    board.make_move("d2d4")

    graph = board.generate_map()

    print("Map Generated!")

    fig, ax = plt.subplots()
    graph.plot_graph(ax)

    print(board.square_positions)

    plt.show()