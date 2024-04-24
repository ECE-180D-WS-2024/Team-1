import sys, os
sys.path.append(os.path.abspath('..'))
from BLE_Module.BLE_Reader import readIMUmultiprocessing, averageValues
from Utilities.decode_orientation import decode_orientation

def ble_imu_decode(x_data, y_data, z_data):
    imu_result = readIMUmultiprocessing(x_data, y_data, z_data)
    linear_accelerations = imu_result["linear_accelerations"]
    #angular_velocities = imu_result["angular_velocities"]
    avg_accelerations = averageValues(linear_accelerations)
    #avg_velocities = averageValues(angular_velocities)
    orientation = decode_orientation(avg_accelerations, None)
    return orientation
