import numpy as np

def cart_2_pol(x, y):
    """
    Returns the polar coordinates of a vector in R2.
    
    """

    r = np.sqrt(x**2 + y**2)
    theta = np.arctan2(y, x)

    return r, theta

def pol_2_cart(r, theta):
    """
    Returns the cartesian coordinates of a vector in R2.
    
    """

    x = r * np.cos(theta)
    y = r * np.sin(theta)

    return x, y


def dist(vec1, vec2):
    """
    Returns the distance between two vectors in R2.
    
    """

    # Calculate the distance
    return np.sqrt((vec2[0] - vec1[0])**2 + (vec2[1] - vec1[1])**2)

def v2v_angle(vec1, vec2):
    """
    Returns the angle between two vectors in R2.
    NOTE: The angle is measured from vec1 to vec2.
    
    """

    ## Calculate the change in x and y
    dx = vec2[0] - vec1[0]
    dy = vec2[1] - vec1[1]

    ## Calculate the angle
    angle = np.arctan2(dy, dx)

    return angle

def transform_polar(vec, r, theta):
    """
    Returns a vector in R2 that is r units away from vec at an angle theta.
    
    """
    # Calculate the transformation
    x_new = vec[0] + r * np.cos(theta)
    y_new = vec[1] + r * np.sin(theta)

    return np.array([x_new, y_new])

def cross(vec1, vec2):
    """
    Returns the magnitude of the cross product of two vectors in R2.
    
    """

    return abs(vec1[0] * vec2[1] - vec1[1] * vec2[0])

def zero_to_2pi(angle):
    """
    Converts and angle in the range [-pi, pi] to the range [0, 2pi].
    
    """

    return angle % (2 * np.pi)
