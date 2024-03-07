def readIMU():
    linear_accelerations = []
    angular_velocities = []
    with open("IMU.txt", "r") as f:
        f.readline() # Pass through header
        for line in f:
            l, a = line.split("---")
            linear_accelerations.append([ float(num) for num in l.split(",")])
            angular_velocities.append([ float(num) for num in a.split(",")])
    return {"linear_accelerations": linear_accelerations, "angular_velocities": angular_velocities}

print(readIMU())