import sys, os
sys.path.append(os.path.abspath('..'))
from BLE_Module.BLE_Reader import readIMUmultiprocessing, averageValues
from Utilities.Orientation import Orientation
from Utilities.Direction import Direction
from Utilities.RGB import RGB
from Utilities.Wires import Wires

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
        case default:
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
        case default:
            return Direction.NO_INPUT

def ble_rgb_decode(rgb):
    if (rgb):
        return RGB.PRESSED
    else:
        return RGB.NOT_PRESSED

def ble_wires_decode(wires):
    match wires:
        case 1:
            return Wires.WIRE_1
        case 2:
            return Wires.WIRE_2
        case 3:
            return Wires.WIRE_3
        case 4:
            return Wires.WIRE_4
        case 5:
            return Wires.WIRE_5
        case 6:
            return Wires.WIRE_6
        case default:
            return Wires.NO_PRESS
