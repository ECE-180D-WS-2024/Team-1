import sys, os
sys.path.append(os.path.abspath('..'))
from Utilities.Orientation import Orientation

def decode_orientation(linear_accelerations, angular_velocities):
    x, _, z = linear_accelerations
    if z > 0.8:
        return Orientation.FLAT
    elif z < -0.8:
        return Orientation.UPSIDE_DOWN
    elif x > 0.8:
        return Orientation.ANTENNA_DOWN
    elif x < 0.8:
        return Orientation.ANTENNA_UP
    else:
        return Orientation.UNRECOGNIZED