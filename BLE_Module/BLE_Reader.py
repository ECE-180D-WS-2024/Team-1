import numpy as np

def readIMU():
    linear_accelerations = []
    angular_velocities = []
    with open("BLE_Module/IMU.txt", "r") as f:
        f.readline() # Pass through header
        for line in f:
            l, a = line.split("---")
            linear_accelerations.append([ float(num) for num in l.split(",")])
            angular_velocities.append([ float(num) for num in a.split(",")])
    return {"linear_accelerations": linear_accelerations, "angular_velocities": angular_velocities}

# Expects uniform 2d Array and averages along rows
def averageValues(vals):
    avgs = []
    for val in vals:
        avgs.append(np.mean(val))
        print(np.mean(val))
    return avgs

def readIMUmultiprocessing(x_arr, y_arr, z_arr):
    return {"linear_accelerations": [x_arr, y_arr, z_arr]}



