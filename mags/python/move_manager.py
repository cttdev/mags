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

    def respond(self):
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

        # Plot the graph and path
        fig, axs = plt.subplots()

        # Set the path planner background
        board.plot_background(axs)

        # Plot the pieces
        board.plot_board(axs)

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

            self.astar.plot_path(axs)

        # Plan the move path
        map.clear_points()
        self.astar.set_graph(map)

        self.astar.set_start(start_position)
        self.astar.set_goal(end_position)

        path = self.astar.calculate_path()
        
        board.make_move(best_move)

        # Plot the graph and path
        map.plot_graph(axs, simplify=True)
        self.astar.plot_path(axs)

        # # Return the path
        # return path


if __name__ == "__main__":
    capture_positions = [
        np.array([400, 400]),
        np.array([400, 380]),
        np.array([400, 370]),
        np.array([400, 360]),
    ]

    board = PhysicalBoard(400, 400, 20, 3, capture_positions=capture_positions)
    board.reset()

    astar = Astar()
    astar.clear()

    stockfish = Stockfish(path="stockfish/stockfish_15.1_linux_x64_avx2/stockfish-ubuntu-20.04-x86-64-avx2")

    move_manager = MoveManager(board, astar, stockfish)

    # board.make_move("e2e4")
    board.reset("rnbqk2r/pp3ppp/3p1n2/2bQ4/2Pp1p2/5N2/PP2PPPP/RN2KB1R w KQkq - 2 8")

    path = move_manager.respond()

    path = move_manager.respond()

    plt.show()
