import matplotlib.style as mplstyle

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

        # Prepare the path planner
        self.astar.clear()
        self.astar.set_graph(map)
        
        # Set the start and end points
        self.astar.set_start(start_position)
        self.astar.set_goal(end_position)

        # Plan the path
        path = self.astar.calculate_path()

        # Plot the graph and path
        fig, axs = plt.subplots()
        map.plot_graph(axs)
        self.astar.plot_path(axs)

        plt.pause(0.1)

        # Return the path
        return path


if __name__ == "__main__":
    board = PhysicalBoard(400, 400, 10, 3)
    board.reset()

    astar = Astar()
    astar.clear()

    stockfish = Stockfish(path="stockfish/stockfish_15.1_linux_x64_avx2/stockfish-ubuntu-20.04-x86-64-avx2")

    move_manager = MoveManager(board, astar, stockfish)

    # board.make_move("e2e4")
    board.reset("rnbqkbnr/pp3ppp/4p3/2pp4/2P1P3/3P4/PP3PPP/RNBQKBNR w KQkq - 0 4")

    path = move_manager.respond()

    plt.show()
