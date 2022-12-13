from mags.python.astar.graph import Circle, Node

from utils import dist, transform_polar, v2v_angle


class Astar:
    """
    A class to preform A* path finding on a graph.

    """
    def __init__(self, graph, start, goal):
        self.graph = graph

        self.set_start(start)
        self.set_goal(goal)

    def set_start(self, start):
        """
        Set the start point of the path.

        """
        self.start = self.add_point(start)

    def set_goal(self, goal):
        """
        Set the goal point of the path.
            
        """
        self.goal = self.add_point(goal)

    def add_point(self, point):
        circle = Circle(point, 0)
        node = Node(circle, [0, 0])

        self.graph.add_node(node)

        return node
    
    def get_edge_cost(self, edge):
        """
        Get the cost of an edge.

        """
        first = edge.get_first()
        second = edge.get_second()
        
        # Add 1 to the cost of all edges to favor a path with less nodes
        if edge.is_surfing():
            # If the edge is surfing, the cost is the length
            return 1 + dist(first.position(), second.position())
        else:
            # If the edge is hugging, calculate the arc length
            arc_center = first.get_circle().get_center()
            arc_radius = first.get_circle().get_radius()

            # Get the angle between the two nodes
            angle = v2v_angle(first.position() - arc_center, second.position() - arc_center)

            # Get the radius of the circle
            radius = first.get_circle().get_radius()

            # Calculate the arc length
            arc_length = radius * angle

            return 1 + arc_length

    def get_heuristic(self, node):
        """
        Get the heuristic for a node.

        """
        # A simple heuristic is the distance to the goal
        return dist(node.position(), self.goal.position())