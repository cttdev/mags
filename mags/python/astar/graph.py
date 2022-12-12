from matplotlib import pyplot as plt
import numpy as np

from utils import dist, transform_polar, v2v_angle


class Circle:
    """
    Class to represent circles.
    Stores the radius and center of the circle.

    """

    def __init__(self, r, center):
        self.r = r
        self.center = center

    def get_r(self):
        return self.r

    def get_center(self):
        return self.center

class Node:
    """
    Class that represents a node in the graph. Stores the circle the node is on and its (x, y) postion.

    """

    def __init__(self, circle, position):
        self.circle = circle
        self.position = position

    def get_circle(self):
        return self.circle

    def get_position(self):
        return self.position

    def get_x(self):
        return self.position[0]

    def get_y(self):
        return self.position[1]


class Edge:
    """
    Class that represents an edge in the graph. This is a line segment or arc between two nodes.
    NOTE: Surfing edges are line segments, while hugging edges are arcs.
    """

    def __init__(self, first, second):
        self.first = first
        self.second = second

    def get_first(self):
        return self.first

    def get_second(self):
        return self.second

class Graph:
    def __init__(self):
        self.nodes = {}
        self.circles = {}

        self.edges = []

    def add_node(self, node):
        circle = node.get_circle()
        self.circles[id(circle)] = circle
        self.nodes[id(node)] = node

    def add_edge(self, edge):
        # Check if the edge intersects any of the circles in the graph
        if not self.check_intersection(edge):
            self.edges.append(edge)

    def check_intersection(self, edge):
        """
        Checks if an edge intersects any of the circles in the graph.

        """
        circles_to_ignore = [edge.get_first().get_circle(), edge.get_second().get_circle()]

        for circle in self.circles.values():
            if circle in circles_to_ignore:
                continue

            if self.check_circle_intersection(circle, edge):
                return True

        return False


    def add_internal_bitangets(self, circle1, circle2):
        """
        Generates the internal bitangents between two circles.

        NOTE: circle1 is A and circle2 is B.
        """
        # Unpack the circle centers and radii
        A = circle1.get_center()
        B = circle2.get_center()

        r1 = circle1.get_r()
        r2 = circle2.get_r()

        # Calculate the internal bitangent angle, theta
        d = dist(A, B)
        theta = np.arccos((r1 + r2) / d)

        # Calclate the AB and BA angles
        angle_AB = v2v_angle(A, B)
        angle_BA = v2v_angle(B, A)

        # Calculate the internal bitanget points: C, D, E and F
        # Nodes on circle 1: C and D
        C = transform_polar(A, r1, angle_AB + theta)
        D = transform_polar(A, r1, angle_AB - theta)

        # Nodes on circle 2: E and F
        E = transform_polar(B, r2, angle_BA - theta)
        F = transform_polar(B, r2, angle_BA + theta)

        # Create nodes
        C_node = Node(circle1, C)
        D_node = Node(circle1, D)

        E_node = Node(circle2, E)
        F_node = Node(circle2, F)

        # Add nodes to graph
        self.add_node(C_node)
        self.add_node(D_node)

        self.add_node(E_node)
        self.add_node(F_node)

        # Generate the first edge
        self.add_edge(Edge(D_node, E_node))

        if (r1 > 0 and r2 > 0):
            # Generate the second internal bitangent edge if both circles have non zero radi
            self.add_edge(Edge(C_node, F_node))

    def add_external_bitangets(self, circle1, circle2):
        """
        Generates the external bitangents between two circles.

        NOTE: circle1 is A and circle2 is B.
        """
        # Unpack the circle centers and radii
        A = circle1.get_center()
        B = circle2.get_center()

        r1 = circle1.get_r()
        r2 = circle2.get_r()

        # Calculate the internal bitangent angle, theta
        d = dist(A, B)
        theta = np.arccos(abs(r1 - r2) / d)

        # Calclate the AB and BA angles
        angle_AB = v2v_angle(A, B)
        angle_BA = v2v_angle(B, A)

        # Calculate the internal bitanget points: C, D, E and F
        # Nodes on circle 1: C and D
        C = transform_polar(A, r1, angle_AB + theta)
        D = transform_polar(A, r1, angle_AB - theta)

        # Nodes on circle 2: E and F
        # NOTE: We use "angle AB" instead of BA because theta is measured from AB. BA is opposite to AB so we need to add pi to it.
        # angle_AB = angle_BA + np.pi
        E = transform_polar(B, r2, (angle_BA + np.pi) - theta)
        F = transform_polar(B, r2, (angle_BA + np.pi) + theta)

        # Create nodes
        C_node = Node(circle1, C)
        D_node = Node(circle1, D)

        E_node = Node(circle2, E)
        F_node = Node(circle2, F)

        # Add nodes to graph
        self.add_node(C_node)
        self.add_node(D_node)

        self.add_node(E_node)
        self.add_node(F_node)

        if (r1 > 0 or r2 > 0):
            # Generate the first external bitangent edge if either circle has a non zero radius
            # This is to avoid creating duplicate edges with the internal bitangents
            self.add_edge(Edge(D_node, E_node))

        if (r1 > 0 and r2 > 0):
            # Generate the second internal bitangent edge if both circles have non zero radi
            self.add_edge(Edge(C_node, F_node))

    def plot_graph(self, axs):
        """
        Plots the graph on the given axes.
        """
        # Set square aspect ratio
        axs.set_aspect('equal')

        # Plot the circles
        for circle in self.circles.values():
            axs.add_patch(plt.Circle(circle.get_center(), circle.get_r(), fill=False))

        # Plot the edges
        for edge in self.edges:
            first = edge.get_first()
            second = edge.get_second()

            axs.plot([first.get_x(), second.get_x()], [first.get_y(), second.get_y()], 'b-')

        # Plot the nodes
        for node in self.nodes.values():
            axs.plot(node.get_x(), node.get_y(), 'ro')

    @staticmethod
    def check_circle_intersection(circle, edge):
        """
        Checks if the given edge intersects the given circle.
        Returns True if the edge intersects the circle, False otherwise.

        """
        # Unpack the circle parameters
        center = circle.get_center()
        r = circle.get_r()

        pos1 = edge.get_first().get_position()
        pos2 = edge.get_second().get_position()

        # Calculate the distance between the edge and the circle center
        # Creates a parallelogram where the edge is the base and the circle lies on one of the corners with:
        # 1. A vector from the start of the edge to the end of the edge
        # 2. A vector from the start of the edge to the circle center
        # So, the distance is the height of the parallelogram and the length of the edge is the base
        # The area of the parallelogram (b * h) is the norm of the cross product of the two vectors

        # We also need to determine if the point is over the edge of the line segment or not
        # We can do this by taking the dot product of a vector from the start to the center of the circle and a vector from the start to the end
        # If the dot product is negative, the point is on the other side of the line segment
        # We can do the same for the end of the line segment taking the dot product of a vector from the end to the center of the circle and a vector from the end to the start
        # If the dot product is negative, the point is on the other side of the line segment
        # If either dot product is negative, we set the distannce equal to the distance between the circle center and the closest point on the line segment (either the start or the end)
        
        # Check if circle is over the edge:
        # If np.dot(center - pos1, pos2 - pos1) < 0 then d = dist(center, pos1)
        # If np.dot(center - pos2, pos1 - pos2) < 0 then d = dist(center, pos2)
        if (np.dot(center - pos1, pos2 - pos1) < 0):
            d = dist(center, pos1)
        elif (np.dot(center - pos2, pos1 - pos2) < 0):
            d = dist(center, pos2)
        else:
            # Check the distance from the circle to the edge
            # A = b * h
            # b = |pos2 - pos1|
            # A = |(pos2 - pos1) x (center - pos1)|
            # h = A / b
            # h = |(pos2 - pos1) x (center - pos1)| / |pos2 - pos1|
            d = np.linalg.norm(np.cross(pos2 - pos1, center - pos1)) / dist(pos2, pos1)

        # Check if the edge intersects the circle
        if (d <= r):
            return True
        else:
            return False

if __name__ == "__main__":
    # Testing Two Circles
    # circle1 = Circle(1, np.array([0, 0]))
    # circle2 = Circle(1, np.array([-3, -3]))

    # graph = Graph()
    # graph.add_internal_bitangets(circle1, circle2)
    # graph.add_external_bitangets(circle1, circle2)

    # fig, axs = plt.subplots()
    # graph.plot_graph(axs)

    # Testing Grid of Circles
    graph = Graph()

    grid_dims = np.array([8, 8])
    grid_spacing = 1

    circle_radius = 0.1

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

    print("Generated Graph!")

    fig, axs = plt.subplots()
    graph.plot_graph(axs)

    plt.show()