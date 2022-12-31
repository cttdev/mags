import numpy as np
from matplotlib import pyplot as plt
from planning.astar import Astar
from planning.board import PhysicalBoard

from stockfish import Stockfish


class MoveManager():
    """
    A class that hooks into stockfish to manage the path planning and board state handling for the robot.

    """

    def __init__(self, board: PhysicalBoard, astar: Astar, stockfish: Stockfish):
        self.board = board
        self.astar = astar

        self.stockfish = stockfish

    def respond(self, plotting_axs=None):
        """
        Respond to the current board state.

        """
        # Get the current board state
        fen = self.board.get_fen()

        # Get the best move UCI from stockfish
        self.stockfish.set_fen_position(fen)
        best_move = self.stockfish.get_best_move()

        # Get the start and end squares
        # Read the UCI string from the start to account for promtion
        start_square = best_move[:2]
        end_square = best_move[2:4]

        # Get the start and end positions
        start_position = self.board.get_square_position(start_square)
        end_position = self.board.get_square_position(end_square)

        # Generate the board map
        map = self.board.generate_map([start_square, end_square])

        # Plot the board
        if plotting_axs is not None:
            # Set the path planner background
            board.plot_background(plotting_axs)

            # Plot the pieces
            board.plot_board(plotting_axs)

        # Setup a vaiable to hold the capture path
        capture_path = None

        # Check if move is capture
        if self.board.check_capture(best_move):
            # If the move is a capture, remove the piece from the board
            # Prepare the path planner
            map.clear_points()
            self.astar.set_graph(map)
        
            # Set the start and end points
            self.astar.set_start(end_position)
            self.astar.set_goal(self.board.get_open_capture_position())

            # Plan the path
            capture_path = self.astar.calculate_path()

            # Plot the capture path
            if plotting_axs is not None:
                self.astar.plot_path(plotting_axs, board.get_piece_diameter())

        # Plan the move path
        map.clear_points()
        self.astar.set_graph(map)

        self.astar.set_start(start_position)
        self.astar.set_goal(end_position)

        path = self.astar.calculate_path()
        
        # Make the move on the board
        board.make_move(best_move)
        
        # Plot the graph and the move path
        if plotting_axs is not None:
            map.plot_graph(plotting_axs, simplify=False)
            self.astar.plot_path(plotting_axs, board.get_piece_diameter())

        # Return the path
        return [capture_path, path]


if __name__ == "__main__":
    capture_positions = [
        np.array([410, 400]),
        np.array([410, 380]),
        np.array([410, 370]),
        np.array([410, 360]),
    ]

    board = PhysicalBoard(400, 400, 23, 2, capture_positions=capture_positions)
    board.reset()

    astar = Astar()
    astar.clear()

    stockfish = Stockfish(path="stockfish/stockfish_15.1_linux_x64_avx2/stockfish-ubuntu-20.04-x86-64-avx2")

    move_manager = MoveManager(board, astar, stockfish)

    # board.make_move("e2e4")
    board.reset("rnbqk2r/pp3ppp/3p1n2/2bQ4/2Pp1p2/5N2/PP2PPPP/RN2KB1R w KQkq - 2 8")

    fig, ax = plt.subplots()

    path = move_manager.respond(ax)

    # fig, axs = plt.subplots(2, 5)

    # for i in range(10):
    #     path = move_manager.respond(axs[int(np.floor(i / 5)), i % 5])

    plt.show()
