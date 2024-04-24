import sys, os
sys.path.append(os.path.abspath('..'))
from BLE_Module.BLE_Reader import readIMUmultiprocessing, averageValues
from Utilities.decode_orientation import decode_orientation

def ble_imu_decode(sharedArr):
    imu_result = readIMUmultiprocessing(sharedArr)
    linear_accelerations = imu_result["linear_accelerations"]
    angular_velocities = imu_result["angular_velocities"]
    avg_accelerations = averageValues(linear_accelerations)
    avg_velocities = averageValues(angular_velocities)
    orientation = decode_orientation(avg_accelerations, avg_velocities)
    return orientation
