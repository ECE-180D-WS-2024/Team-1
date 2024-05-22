from .Orientation import Orientation
from .Direction import Direction

def ble_imu_decode(orientation):
    match orientation:
        case 0:
            return Orientation.FLAT
        case 1:
            return Orientation.UPSIDE_DOWN
        case 2:
            return Orientation.ANTENNA_DOWN
        case 3:
            return Orientation.ANTENNA_UP
        case _:
            return Orientation.UNRECOGNIZED

def ble_direction_decode(direction):
    match direction:
        case 1:
            return Direction.UP
        case 2:
            return Direction.LEFT
        case 3:
            return Direction.RIGHT
        case 4:
            return Direction.DOWN
        case _:
            return Direction.NO_INPUT

