from collections import UserList
from itertools import compress
from multiprocessing import Pool, cpu_count
from matplotlib import pyplot as plt
from matplotlib.patches import Arc
import numpy as np

from .utils import cross, dist, dot, transform_polar, v2v_angle, zero_to_2pi


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
    Class that represents a node in the graph. Stores the circle the node is on and its (x, y) position.

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

    def __lt__(self, other):
        """
        Implements the less than operator for nodes.
        NOTE: This is used to compare nodes in the priority queue.
        If two nodes have the same priority, the one with the lower id is considered to be less than the other.
        TODO: Bit sus?
        """
        return id(self) < id(other)


class Edge(UserList):
    """
    Class that represents an edge in the graph. This is a line segment or arc between two nodes.
    NOTE: Surfing edges are line segments, while hugging edges are arcs.
    """

    def __init__(self, first, second, is_surfing):
        self.data = [first, second]

        self.surfing = is_surfing

    def get_first(self):
        return self[0]

    def get_second(self):
        return self[1]

    def is_surfing(self):
        return self.surfing

    def check_equivalence(self, other):
        """
        Checks if two edges are equivalent.
        Two edges are equivalent if they have the same nodes in the same order.

        """
        return (self.get_first() == other.get_first() and self.get_second() == other.get_second()) or (self.get_first() == other.get_second() and self.get_second() == other.get_first())

class Graph:
    def __init__(self, circles):
        self.nodes = {}
        self.circles = {}

        self.surfing_edges = []
        self.hugging_edges = []

        self.points = []
        self.point_circles = []
        self.tangent_edges = [] # Store the tangent edges separately to allow of easy modification of the graph

        # Add the circles to the graph
        for circle in circles:
            for other_circle in circles:
                if circle == other_circle:
                    continue
                
                # Add internal and external bitangents between circles
                self.add_internal_bitangents(other_circle, circle)
                self.add_external_bitangents(other_circle, circle)

    def prepare(self):
        """
        Prepares a graph for searching

        NOTE: This should only be called once after the graph is fully constructed.

        """

        # Clean up the surfing edge intersections
        self.clean_surfing_edges()

        # Add hugging edges
        self.add_hugging_edges()

        # Edge optimization
        self.prepare_edge_optimization()

    def get_nodes(self):
        return self.nodes
    
    def get_circles(self):
        return self.circles
    
    def get_edges(self):
        return self.surfing_edges + self.tangent_edges + self.hugging_edges

    def clear(self):
        self.nodes.clear()
        self.circles.clear()

        self.surfing_edges.clear()
        self.hugging_edges.clear()
    
    def clear_points(self):
        """
        Removes all points from the graph.

        """
        for point in self.points:
            self.nodes.pop(id(point))

        for circle in self.point_circles:
            self.circles.pop(id(circle))

        self.points.clear()
        self.point_circles.clear()
        self.tangent_edges.clear()

    def prepare_edge_optimization(self):
        """
        Generates a numpy array of the final edges for speedups.
        """

        # Generate np_edges for optimization
        self.np_edges = np.array(self.get_edges())

    def get_neighbors(self, node):
        """
        Returns the neighbors of a node on the graph.
        Returns a list of tuples of the form (node, edge).

        """
        # Check if graph has been prepared
        if not hasattr(self, 'np_edges'):
            raise Exception('Graph has not been prepared for searching. Call prepare() before searching!')

        neighbors = []

        # Get the indicies of the edges that contain the node
        node_indicies = np.where(self.np_edges == node)

        # Get the neighbors
        for i in range(len(node_indicies[0])):
            node_row = node_indicies[0][i]
            node_col = node_indicies[1][i]
            
            # If the node is the first node in the edge, the second node is the neighbor
            if node_col == 0:
                neighbors.append((self.np_edges[node_row][1], self.get_edges()[node_row]))
            # If the node is the second node in the edge, the first node is the neighbor
            else:
                neighbors.append((self.np_edges[node_row][0], self.get_edges()[node_row]))

        # # Slow Method
        # for edge in self.get_edges():
        #     if edge.get_first() == node:
        #         neighbors.append((edge.get_second(), edge))
        #         print("hi")
        #     elif edge.get_second() == node:
        #         neighbors.append((edge.get_first(), edge))
        #         print("low")

        return neighbors

    def add_node(self, node):
        circle = node.get_circle()
        self.circles[id(circle)] = circle
        self.nodes[id(node)] = node

    def add_edge(self, edge):
        # If the edge is hugging, automatically append it
        # Or, if the edge is surfing, check if the edge intersects any of the circles in the graph
        if not edge.is_surfing():
            self.hugging_edges.append(edge)
        else:
            self.surfing_edges.append(edge)

    def clean_surfing_edges(self):
        """
        Removes all edges that intersect any of the circles in the graph.

        """
        with Pool(cpu_count()-1) as pool: 
            self.surfing_edges = list(compress(self.surfing_edges, pool.map(self.check_intersection, self.surfing_edges)))

        with Pool(cpu_count()-1) as pool: 
            self.tangent_edges = list(compress(self.tangent_edges, pool.map(self.check_intersection, self.tangent_edges)))

        self.prepare_edge_optimization()

        # Remove nodes that are no longer connected to any other nodes
        self.remove_unconnected_nodes() # TODO: Very slow

    def remove_unconnected_nodes(self):
        """
        Removes all nodes that are no longer connected to any other nodes.

        """
        # Create a copy of the nodes dictionary
        new_nodes = self.nodes.copy()

        # Remove all nodes that are not connected to any other nodes
        for node in self.nodes.values():
            if len(self.get_neighbors(node)) == 0:
                new_nodes.pop(id(node))

        # Update the nodes dictionary
        self.nodes = new_nodes

    def check_intersection(self, edge):
        """
        Checks if an edge intersects any of the circles in the graph.

        Returns True if the edge does not intersect any of the circles in the graph.

        """
        circles_to_ignore = [edge.get_first().get_circle(), edge.get_second().get_circle()]

        for circle in self.circles.values():
            if circle in circles_to_ignore:
                continue

            if self.check_circle_intersection(circle, edge):
                return False

        return True

    def add_point(self, node):
        """
        Inserts a point (circle with radius 0) into the graph.
        NOTE: This updates the surfing and hugging edges.

        """
        # Keep track of which nodes are points
        self.points.append(node)
        self.point_circles.append(node.get_circle())

        # Add the node and its circle to the graph
        self.add_node(node)

        # Add internal bitangents to the point
        for other_circle in self.circles.values():
            if other_circle == node.get_circle():
                continue
                
            # We only need to add internal bitangents for points
            self.add_tangents(node, other_circle)

        return node

    def add_tangents(self, point_node, circle):
        """
        Generates the tangents between a point and a circle
        
        """
        # Unpack the circle center and radius
        A = point_node.get_position()
        B = circle.get_center()
        r = circle.get_r()

        # First check if the second circle is a point
        if r == 0:
            # If so, connect the two nodes
            # Find the node on the circle
            for node in self.nodes.values():
                if node.get_circle() == circle:
                    circle_node = node
                    break
                    
            # Generate the edge
            edge = Edge(point_node, circle_node, True)
            
            # Check if the edge already exists
            for other_edge in self.surfing_edges:
                if edge.check_equivalence(other_edge):
                    return
            
            # Add the edge
            self.tangent_edges.append(edge)
            return

    
        # Calculate the internal bitangent angle, theta
        d = dist(A, B)
        theta = np.arccos(r / d)

        # Calculate the AB and BA angles
        angle_BA = v2v_angle(B, A)

        # Calculate the internal bitangent points: E and F
        # Nodes on circle : E and F
        E = transform_polar(B, r, angle_BA - theta)
        F = transform_polar(B, r, angle_BA + theta)

        # Create nodes
        E_node = Node(circle, E)
        F_node = Node(circle, F)

        # Add nodes to graph
        self.add_node(E_node)
        self.add_node(F_node)

        # Generate the internal bitangent edges
        self.tangent_edges.append(Edge(point_node, E_node, True))
        self.tangent_edges.append(Edge(point_node, F_node, True))
        

    def add_internal_bitangents(self, circle1, circle2):
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

        # Calculate the AB and BA angles
        angle_AB = v2v_angle(A, B)
        angle_BA = v2v_angle(B, A)

        # Calculate the internal bitangent points: C, D, E and F
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

        # Generate the internal bitangent edges
        self.add_edge(Edge(D_node, E_node, True))
        self.add_edge(Edge(C_node, F_node, True))

    def add_external_bitangents(self, circle1, circle2):
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

        # Calculate the AB and BA angles
        angle_AB = v2v_angle(A, B)
        angle_BA = v2v_angle(B, A)

        # Calculate the internal bitangent points: C, D, E and F
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
        
        # Generate external bitangent edges
        self.add_edge(Edge(D_node, E_node, True))
        self.add_edge(Edge(C_node, F_node, True))

    def add_hugging_edges(self):
        """
        Updates the hugging edges in the graph.
        """
        # Remove all the hugging edges
        self.hugging_edges = []

        # Sort the nodes by circle
        nodes_by_circle = {}
        for node in self.nodes.values():
            circle = node.get_circle()
            if circle.get_r() == 0:
                # Ignore nodes on a circle with zero radius
                continue

            if circle not in nodes_by_circle:
                nodes_by_circle[circle] = []

            nodes_by_circle[circle].append(node)

        # Order the nodes by angle
        def get_angle(circle, node):
            # Get the v2v angle between the circle center and the node (range [-pi, pi])
            angle = v2v_angle(circle.get_center(), node.get_position())

            # Convert the angle to the range [0, 2pi]
            angle = zero_to_2pi(angle)

            return angle

        # Sort the nodes on each circle by angle
        for circle in nodes_by_circle.keys():
            # Get the nodes on the circle
            circle_nodes = nodes_by_circle[circle]

            # Sort the nodes by angle
            circle_nodes.sort(key=lambda node: get_angle(circle, node))

        # Add the hugging edges
        for circle in nodes_by_circle.keys():
            # Get the nodes on the circle
            nodes = nodes_by_circle[circle]

            # Iterate over the nodes
            for i in range(len(nodes)):
                # Connect the nodes in a circle
                n1 = nodes[i] # Current node
                n2 = nodes[(i + 1) % len(nodes)] # Next node (wraps around to the first node when the current node is the last node)

                self.add_edge(Edge(n1, n2, False))    

    def plot_graph(self, ax, simplify=True):
        """
        Plots the graph on the given axes.
        """
        # Set square aspect ratio
        ax.set_aspect("equal")

        # Plot the circles
        for circle in self.circles.values():
            ax.add_patch(plt.Circle(circle.get_center(), circle.get_r(), fill=False))

        if not simplify:
            # Plot the surfing edge lines
            # count = 0
            for edge in self.surfing_edges + self.tangent_edges:
                first = edge.get_first()
                second = edge.get_second()

                ax.plot([first.get_x(), second.get_x()], [first.get_y(), second.get_y()], "b-")

                # # Label the surfing edges
                # ax.text((first.get_x() + second.get_x()) / 2, (first.get_y() + second.get_y()) / 2, str(count), color="b")
                # count += 1

            # Plot the hugging edge arcs
            for edge in self.hugging_edges[::2]:
                first = edge.get_first()
                second = edge.get_second()

                arc_center = first.get_circle().get_center()
                arc_radius = first.get_circle().get_r()

                arc_start = v2v_angle(arc_center, first.get_position())
                arc_end = v2v_angle(arc_center, second.get_position())

                # For plotting we will first transform the angles to be in the range [0, 2pi)
                arc_start = zero_to_2pi(arc_start)
                arc_end = zero_to_2pi(arc_end)

                # Determine the start and end points for plotting and convert the angles to degrees
                theta1 = np.rad2deg(min(arc_start, arc_end))
                theta2 = np.rad2deg(max(arc_start, arc_end))

                # Plot the start and end points
                ax.plot(first.get_x(), first.get_y(), "r*")
                ax.plot(second.get_x(), second.get_y(), "g*")

                ax.add_patch(Arc(arc_center, 2 * arc_radius, 2 * arc_radius, theta1=theta1, theta2=theta2, color="g"))

            # # Plot the nodes
            # for node in self.nodes.values():
            #     ax.plot(node.get_x(), node.get_y(), "ro")

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

        # Check if the edge is a point
        if (pos1 == pos2).all():  
            # # Check if the point is on the circle
            # if np.linalg.norm(pos1 - center) == r:
            #     return True
            # else:
            #     return False

            # It is faster to assume the point lies on another circle and thus cannot intersect this circle
            return False

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
        # If either dot product is negative, we set the distance equal to the distance between the circle center and the closest point on the line segment (either the start or the end)
        
        # Check if circle is over the edge:
        # If np.dot(center - pos1, pos2 - pos1) < 0 then d = dist(center, pos1)
        # If np.dot(center - pos2, pos1 - pos2) < 0 then d = dist(center, pos2)
        if (dot(center - pos1, pos2 - pos1) < 0):
            d = dist(center, pos1)
        elif (dot(center - pos2, pos1 - pos2) < 0):
            d = dist(center, pos2)
        else:
            # Check the distance from the circle to the edge
            # A = b * h
            # b = |pos2 - pos1|
            # A = |(pos2 - pos1) x (center - pos1)|
            # h = A / b
            # h = |(pos2 - pos1) x (center - pos1)| / |pos2 - pos1|
            d = cross(pos2 - pos1, center - pos1) / dist(pos2, pos1)

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
    # graph.add_internal_bitangents(circle1, circle2)
    # graph.add_external_bitangents(circle1, circle2)

    # fig, ax = plt.subplots()
    # graph.plot_graph(ax)

    # Testing Grid of Circles
    graph = Graph([])

    grid_dims = np.array([8, 4])
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
                graph.add_internal_bitangents(i_circle, circle)
                graph.add_external_bitangents(i_circle, circle)

            # Store circle
            circles.append(i_circle)

    graph.add_hugging_edges()

    print("Generated Graph!")

    fig, ax = plt.subplots()
    graph.plot_graph(ax, simplify=False)

    plt.show()
