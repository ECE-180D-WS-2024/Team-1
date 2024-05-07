from enum import Enum

class Orientation(Enum):
    FLAT = 0
    UPSIDE_DOWN = 1
    ANTENNA_DOWN = 2
    ANTENNA_UP = 3
    UNRECOGNIZED = -1