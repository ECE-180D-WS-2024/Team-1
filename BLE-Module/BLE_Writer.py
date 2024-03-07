import asyncio
import time
from bleak import BleakScanner, BleakClient, BleakError

# These need to match defined UUID's for IMU on transmitting Arduino
X_ACCEL_CHAR_UUID = "663fdcf8-2126-464d-a6c1-c882f5477fb7"
Y_ACCEL_CHAR_UUID = "e6ac0344-9aee-49ab-b601-1d26b77cf08c"
Z_ACCEL_CHAR_UUID = "224ad21b-9c75-4e1c-a3f0-51c0c7d0a9a8"
X_ANGULAR_VELO_CHAR_UUID = "4de63bcd-e713-4e28-9392-3cc1d7efbabc"
Y_ANGULAR_VELO_CHAR_UUID = "99c07d47-9018-489b-a937-0d911a61aa69"
Z_ANGULAR_VELO_CHAR_UUID = "85c17e72-fb28-4883-9333-479b20fce5a7"

# General Async Usage Pattern
async def asyncMain():
    BleDev = await asyncFindDevice("Nano 33 IoT")
    print("Found BleDev: " + BleDev.address)
    BleClient = BleakClient(BleDev)
    await BleClient.connect()
    try:
        while True:
            Imu_Readings = await asyncReadIMU(BleClient, numReadings=10)
            if Imu_Readings["success"]:
                print("Writing to file...")
                await writeIMUtoFile(Imu_Readings)
    except KeyboardInterrupt:
        print("here")
        if BleClient.is_connected:
            await BleClient.disconnect()



async def asyncFindDevice(name):
    # Get BLE Device
    BleDev = None
    while BleDev is None:
        BleDev = await BleakScanner.find_device_by_name(name)
        if BleDev is None:
            print("Failed to Find Device! Retrying...")
            devices = await BleakScanner.discover()
            for device in devices:
                print(device)
    return BleDev
    

# Read IMU data
async def asyncReadIMU(client, numReadings=10):
    try:
        linear_accels = []
        angular_velos = []
        for _ in range(numReadings):
            imu_x_accel_arr = await client.read_gatt_char(X_ACCEL_CHAR_UUID)
            imu_y_accel_arr = await client.read_gatt_char(Y_ACCEL_CHAR_UUID)
            imu_z_accel_arr = await client.read_gatt_char(Z_ACCEL_CHAR_UUID)
            imu_x_angular_velo_arr = await client.read_gatt_char(X_ANGULAR_VELO_CHAR_UUID)
            imu_y_angular_velo_arr = await client.read_gatt_char(Y_ANGULAR_VELO_CHAR_UUID)
            imu_z_angular_velo_arr = await client.read_gatt_char(Z_ANGULAR_VELO_CHAR_UUID)

            imu_x_accel = int.from_bytes(imu_x_accel_arr, 'little', signed=True) / 1000.0
            imu_y_accel = int.from_bytes(imu_y_accel_arr, 'little', signed=True) / 1000.0
            imu_z_accel = int.from_bytes(imu_z_accel_arr, 'little', signed=True) / 1000.0
            imu_x_angular_velo = int.from_bytes(imu_x_angular_velo_arr, 'little', signed=True) / 1000.0
            imu_y_angular_velo = int.from_bytes(imu_y_angular_velo_arr, 'little', signed=True) / 1000.0
            imu_z_angular_velo = int.from_bytes(imu_z_angular_velo_arr, 'little', signed=True) / 1000.0

            await client.write_gatt_char(11, bytearray([0]))
                                
            linear_accels.append([imu_x_accel, imu_y_accel, imu_z_accel])
            angular_velos.append([imu_x_angular_velo, imu_y_angular_velo, imu_z_angular_velo])

        return dict({"success": True, "linear_accels": linear_accels, "angular_velos": angular_velos})

    except TimeoutError:
        print("Could not connect before timeout")
        print("This is where everything breaks!")
        return dict({"success": False})
    except BleakError as e:
        print(e)
        return dict({"success": False})

async def toggleLED(BleDev, numToggles):
    # Connect to BLE
    try:
        async with BleakClient(BleDev) as client:
            while(numToggles) > 0:
                # Enumerate Services
                for service in client.services:
                    print(service)
                    # Enumerate Characteristics
                    for characteristic in service.characteristics:
                        print(characteristic)

                data_byte_arr = await client.read_gatt_char(11)
                data_int_val = int.from_bytes(data_byte_arr, "big")
                await client.write_gatt_char(14, bytearray([1])) # Send Heartbeat
                if data_int_val == 1:
                    await client.write_gatt_char(11, bytearray([0]))
                else:
                    await client.write_gatt_char(11, bytearray([1]))
                numToggles -= 1;
                time.sleep(1)
    except TimeoutError as e:
        print("Could not connect before timeout")
        print("This is where everything breaks!")
    except BleakError:
        print("Generic Bluetooth Error")

# Write data to file
async def writeIMUtoFile(IMUData):
    data = [IMUData['linear_accels'], IMUData['angular_velos']]
    with open("IMU.txt", "w") as f:
        f.write("Linear Accelerations (g) x, y, z --- Angular Velocities (dps) rx, ry, rz\r\n")
        for i in range(len(data[0])):
            f.write(str(data[0][i][0]) + ", " + str(data[0][i][1]) + ", " + str(data[0][i][2]) + " --- " + 
                    str(data[1][i][0]) + ", " + str(data[1][i][1]) + ", " + str(data[1][i][2]))
            f.write("\r\n")

if __name__ == "__main__":
    # Run as async
    asyncio.run(asyncMain())       






# General Sync Usage Pattern... Doesn't work
def syncMain():
    findDeviceResult = syncFindDevice("Nano 33 IoT")
    if not findDeviceResult["success"]:
        exit(1)
    print("Found BleDev: " + findDeviceResult["BleDev"].address)
    Imu_Readings = syncReadIMU(findDeviceResult["BleDev"])
    print(Imu_Readings) 
    
# Run an Async Function as Synchronous Function
# func is a lambda with captured arguments
# I.E to run asyncFindDevice Synchronously:
# Define func = lambda: asyncFindDevice("Nano 33 IoT")
def syncRunAsync(func):
    success = True
    result = None
    loop = asyncio.new_event_loop()
    try: 
        result = loop.run_until_complete(func())
    except Exception as e:
        print("Error in " + str(func))
        print(e)
        success = False
    finally:
        loop.close()
    return dict({"success": success, "BleDev": result})

# Get BLE Device Synchronously
def syncFindDevice(name):
    func = lambda: asyncFindDevice(name)
    return syncRunAsync(func)

# ReadIMU Synchronously
def syncReadIMU(BleDev):
    func = lambda: asyncReadIMU(BleDev)
    return syncRunAsync(func)