from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice
from enum import Enum, auto
import struct
import math
import asyncio
import time

X_ACCEL_CHAR_UUID = "663fdcf8-2126-464d-a6c1-c882f5477fb7"
Y_ACCEL_CHAR_UUID = "e6ac0344-9aee-49ab-b601-1d26b77cf08c"
Z_ACCEL_CHAR_UUID = "224ad21b-9c75-4e1c-a3f0-51c0c7d0a9a8"
X_ANGULAR_VELO_CHAR_UUID = "4de63bcd-e713-4e28-9392-3cc1d7efbabc"
Y_ANGULAR_VELO_CHAR_UUID = "99c07d47-9018-489b-a937-0d911a61aa69"
Z_ANGULAR_VELO_CHAR_UUID = "85c17e72-fb28-4883-9333-479b20fce5a7"

class Axis(Enum):
    X = auto()
    Y = auto()
    Z = auto()

class BLEController():
    def __init__(self, device_name: str = "Nano 33 IoT"):
        self.device_name: str = device_name
        pass

    async def discover(self) -> BLEDevice:
        device: BLEDevice = None
        while device is None:
            device = await BleakScanner.find_device_by_name(self.device_name)
        return device

    async def connect(self) -> bool:
        # Discover device
        self.device: BLEDevice = await self.discover()

        # Create client
        self.client: BleakClient = BleakClient(self.device)
        return await self.client.connect()
    
    def read_accelerometer_axis(self, axis: Axis) -> bytearray:
        char_uuid: str = ''
        match axis:
            case Axis.X:
                char_uuid = X_ACCEL_CHAR_UUID
            case Axis.Y:
                char_uuid = Y_ACCEL_CHAR_UUID
            case Axis.Z:
                char_uuid = Z_ACCEL_CHAR_UUID
        return self.client.read_gatt_char(char_uuid)

    async def read_accelerometer(self) -> dict[str, float]:
        data_dict = {'x': -math.inf, 'y': -math.inf, 'z': -math.inf}
        x_bytes = self.read_accelerometer_axis(Axis.X)
        y_bytes = self.read_accelerometer_axis(Axis.Y)
        z_bytes = self.read_accelerometer_axis(Axis.Z)

        x = struct.unpack('f', await x_bytes)
        y = struct.unpack('f', await y_bytes)
        z = struct.unpack('f', await z_bytes)

        data_dict['x'] = x
        data_dict['y'] = y
        data_dict['z'] = z
        
        return data_dict
    
    def read_gyro_axis(self, axis: Axis) -> bytearray:
        char_uuid: str = ''
        match axis:
            case Axis.X:
                char_uuid = X_ANGULAR_VELO_CHAR_UUID
            case Axis.Y:
                char_uuid = Y_ANGULAR_VELO_CHAR_UUID
            case Axis.Z:
                char_uuid = Z_ANGULAR_VELO_CHAR_UUID
        return self.client.read_gatt_char(char_uuid)

    async def read_gyro(self) -> dict[str, float]:
        data_dict = {'x': math.nan, 'y': math.nan, 'z': math.nan}
        x_bytes = self.read_gyro_axis(Axis.X)
        y_bytes = self.read_gyro_axis(Axis.Y)
        z_bytes = self.read_gyro_axis(Axis.Z)

        t0 = time.time()
        x_bytes = await x_bytes
        # async_vals = await asyncio.gather(x_bytes, y_bytes, z_bytes)
        t1 = time.time()
        print(f'took {(t1 - t0) * 1000}ms')
        x = struct.unpack('f', x_bytes)


        #x = struct.unpack('f', async_vals[0])
        y = 0
        z = 0
        #y = struct.unpack('f', async_vals[1])
        #z = struct.unpack('f', async_vals[2])

        data_dict['x'] = x
        data_dict['y'] = y
        data_dict['z'] = z
        
        return data_dict

async def main():
    controller = BLEController()
    if await controller.connect():
        while True:
            await controller.read_gyro()
    else:
        print("could not connect!")

if __name__ == '__main__':
    asyncio.run(main())
