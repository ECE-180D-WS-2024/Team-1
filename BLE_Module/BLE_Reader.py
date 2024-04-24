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

# Expects uniform 2d Array and averages along columns
def averageValues(vals):
    print(vals)
    return np.mean(vals[len(vals) - 10 : len(vals) ], 0)

def readIMUmultiprocessing(sharedArr):
    linear_accelerations = sharedArr[0]
    angular_velocities = sharedArr[1]
    return {"linear_accelerations": linear_accelerations, "angular_velocities": angular_velocities}



