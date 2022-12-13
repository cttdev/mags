from matplotlib import pyplot as plt
from matplotlib.patches import Arc
import numpy as np
from mags.python.planning.graph import Circle, Graph, Node
from queue import PriorityQueue

from utils import dist, v2v_angle


class Astar:
    """
    A class to preform A* path finding on a graph.

    """
    def __init__(self, graph, start, goal):
        self.graph = graph

        self.frontier = PriorityQueue()

        self.explored = {}
        self.cost = {}

        self.path = None

        self.set_start(start)
        self.set_goal(goal)

    def set_start(self, start):
        """
        Set the start point of the path.

        """
        start_circle = Circle(0, start)
        self.start = Node(start_circle, start)

        graph.add_point(self.start)

    def set_goal(self, goal):
        """
        Set the goal point of the path.
            
        """
        goal_circle = Circle(0, goal)
        self.goal = Node(goal_circle, goal)

        graph.add_point(self.goal)

    def set_graph(self):
        """
        Set the graph to be searched.

        """
        self.graph = graph
    
    def get_edge_cost(self, edge):
        """
        Get the cost of an edge.

        """
        first = edge.get_first()
        second = edge.get_second()
        
        # Add 1 to the cost of all edges to favor a path with less nodes
        if edge.is_surfing():
            # If the edge is surfing, the cost is the length
            return 1 + dist(first.get_position(), second.get_position())
        else:
            # If the edge is hugging, calculate the arc length
            arc_center = first.get_circle().get_center()

            # Get the angle between the two nodes
            start = v2v_angle(arc_center, first.get_position())
            end = v2v_angle(arc_center, second.get_position())

            # Get the angle between the two nodes
            angle = end - start

            # Get the radius of the circle
            radius = first.get_circle().get_r()

            # Calculate the arc length
            arc_length = radius * angle

            return 1 + abs(arc_length)

    def get_heuristic(self, node):
        """
        Get the heuristic for a node.

        """
        # A simple heuristic is the distance to the goal
        return dist(node.get_position(), self.goal.get_position())

    def clear(self):
        """
        Clear the frontier and explored sets.

        """
        self.frontier.queue.clear()
        self.explored.clear()
        self.cost.clear()

        self.path = None

    def calculate_path(self):
        """
        Generates the path from the start to the goal.

        """
        # Clear the frontier and explored sets
        self.clear()

        # Initialize the frontier (The nodes to be explored)
        self.frontier.put((0, self.start))

        # Initialize the explored set (The nodes that have been explored)
        self.explored[self.start] = None

        # Initialize the cost of the path at each node
        self.cost[self.start] = 0

        # Run the search while there are still notes to explore
        while not self.frontier.empty():
            # Get the next node to explore
            _, current = self.frontier.get()

            # If the current node is the goal, return the path
            if current == self.goal:
                break

            # Get the neighbors of the current node
            neighbors = self.graph.get_neighbors(current)

            for neighbor_node, neighbor_edge in neighbors:
                # Get the cost of the neightbor
                neighbor_cost = self.cost[current] + self.get_edge_cost(neighbor_edge)

                # If the neighbor has not been explored or the new cost is less than the old cost
                if neighbor_node not in self.cost or neighbor_cost < self.cost[neighbor_node]:
                    # Update the cost of the path to the neighbor
                    self.cost[neighbor_node] = neighbor_cost

                    # Add the neighbor to the explored set
                    self.explored[neighbor_node] = current

                    # Calculate the priority of the neighbor
                    priority = neighbor_cost + self.get_heuristic(neighbor_node)

                    # Add the neighbor to the frontier
                    self.frontier.put((priority, neighbor_node))

        print("Path found")
        
        # Reconstruct the path
        path = []

        # Start at the goal
        current = self.goal

        # Add the nodes to the path until we reach the beginning
        while current != self.start:
            path.append(current)
            current = self.explored[current]

        # Add the start node
        path.append(self.start)

        # Reverse the path
        path.reverse()

        self.path = path

        return path

    def plot_path(self, axs):
        if self.path is None:
            print("No path found!")
            return
        
        # Plot the path
        for i in range(len(self.path)):
            node = self.path[i]
            next_node = self.path[i + 1] if i < len(self.path) - 1 else None

            if next_node is not None:
                if node.get_circle() == next_node.get_circle():
                    # Hugging Edge
                    circle = node.get_circle()
                    arc_center = circle.get_center()
                    arc_radius = circle.get_r()

                    # Get the angle between the two nodes
                    arc_start = v2v_angle(arc_center, node.get_position())
                    arc_end = v2v_angle(arc_center, next_node.get_position())

                    axs.add_patch(Arc(arc_center, 2 * arc_radius, 2 * arc_radius, theta1=np.rad2deg(arc_start), theta2=np.rad2deg(arc_end), color="orange", linewidth=4))
                else:
                    # Surfing Edge
                    axs.plot([node.get_position()[0], next_node.get_position()[0]], [node.get_position()[1], next_node.get_position()[1]], "orange", linewidth=4)

            
            if node == self.start:
                axs.plot(node.get_position()[0], node.get_position()[1], color="lightcoral", marker="o")
            elif node == self.goal:
                axs.plot(node.get_position()[0], node.get_position()[1], color="mediumpurple", marker="o")


if __name__ == "__main__":
    # # Testing Two Circles
    # circle1 = Circle(1, np.array([0, 0]))
    # circle2 = Circle(1, np.array([3, 3]))

    # # Create graph
    # graph = Graph()

    # # Add circles to graph
    # graph.add_internal_bitangets(circle1, circle2)
    # graph.add_external_bitangets(circle1, circle2)

    # Testing Grid of Circles
    graph = Graph()

    grid_dims = np.array([8, 4])
    grid_spacing = 1

    circle_radius = 0.2

    # Generate grid of circles
    circles = []
    for i in range(0, grid_dims[0]):
        for j in range(0, grid_dims[1]):
            # Generate circle
            i_circle = Circle(circle_radius, np.array([i * grid_spacing, j * grid_spacing]))

            # Add internal and external bitangents between all circles
            for circle in circles:
                graph.add_internal_bitangets(i_circle, circle)
                graph.add_external_bitangets(i_circle, circle)

            # Store circle
            circles.append(i_circle)

    graph.clean_surfing_edges()

    # Initialize A*
    astar = Astar(graph, np.array([0.5, 0.5]), np.array([6.5, 1]))

    print("Calculating Path...")
    # Calculate path
    print(astar.calculate_path())

    # Setup plotting
    fig, axs = plt.subplots()

    # Plot graph
    graph.plot_graph(axs)

    # Plot path
    astar.plot_path(axs)
    
    plt.show()