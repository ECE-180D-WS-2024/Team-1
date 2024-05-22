from .Orientation import Orientation
from .Direction import Direction
from .RGB import RGB
from .Wires import Wire
from .Sequence import Sequence

def ble_imu_decode(orientation):
    match orientation:
        case 0:
            return Orientation.CLOCK
        case 1:
            return Orientation.SPEECH
        case 2:
            return Orientation.LOCALIZATION
        case 3:
            return Orientation.SEQUENCING
        case 4:
            return Orientation.WIRES
        case _:
            return Orientation.OTHER

def ble_direction_decode(direction):
    match direction:
        case 1:
            return Direction.TOP_RIGHT
        case 2:
            return Direction.BOTTOM_RIGHT
        case 3:
            return Direction.TOP_LEFT
        case 4:
            return Direction.BOTTOM_LEFT
        case _:
            return Direction.NO_INPUT

def ble_rgb_decode(rgb):
    if (rgb):
        return RGB.PRESSED
    else:
        return RGB.NOT_PRESSED

def ble_wires_decode(wires):
    match wires:
        case 1:
            return Wire.WIRE_1
        case 2:
            return Wire.WIRE_2
        case 3:
            return Wire.WIRE_3
        case 4:
            return Wire.WIRE_4
        case 5:
            return Wire.WIRE_5
        case 6:
            return Wire.WIRE_6
        case _:
            return Wire.NO_PRESS

def ble_sequence_decode(sequence):
    match sequence:
        case 1:
            return Sequence.TOP_LEFT
        case 2:
            return Sequence.TOP_RIGHT
        case 3:
            return Sequence.BOTTOM_LEFT
        case 4:
            return Sequence.BOTTOM_RIGHT
        case _:
            return Sequence.NO_PRESS