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

# General Usage Pattern
async def main():
    BleDev = await findDevice("Nano 33 IoT")
    print("Found BleDev: " + BleDev.address)
    Imu_Readings = await readIMU(BleDev)
    print(Imu_Readings)

async def findDevice(name):
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
async def readIMU(BleDev):
    try:
        async with BleakClient(BleDev) as client:
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
                            
            linear_accels = [imu_x_accel, imu_y_accel, imu_z_accel]
            angular_velos = [imu_x_angular_velo, imu_y_angular_velo, imu_z_angular_velo]

            return dict({"status": "success", "linear_accels": linear_accels, "angular_velos": angular_velos})

    except TimeoutError:
        print("Could not connect before timeout")
        print("This is where everything breaks!")
        return dict({"status": "failure"})
    except BleakError as e:
        print(e)
        return dict({"status": "failure"})


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

# Currently Async... Thinking about adding synchronous option
asyncio.run(main())