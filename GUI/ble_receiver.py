from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice
from enum import Enum, auto
from multiprocessing import Process, Value
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


ORIENTATION_CHAR_UUID = "ba90a02e-9acd-4f6b-8d2d-db52abdab1ab"
DIRECTION_CHAR_UUID = "2e1c9e14-a3d6-41d6-a484-114375527aa6"
WIRE_CHAR_UUID = "5101a8d5-e8da-4ef6-9e03-1c0573d25429"
TIME_CHAR_UUID = "2e92fbab-6365-4ce6-aa19-9b1fe217888c"
START_CHAR_UUID = "d1b05699-f934-43e3-ae5f-2510118995f7"

WINDOW_WIDTH = 10
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
    
    async def read_char(self, char_uuid: str) -> int:
        bytes = await self.client.read_gatt_char(char_uuid)
        val = int.from_bytes(bytes, "little", signed=True)
        return val
    
    
    async def read_into_mem(self, shared_arr: list[float], axis: Axis, idx: int):
        bytes = await self.read_accelerometer_axis(axis)
       # t0 = time.time()
        #t1 = time.time()
        #print(f'took {(t1 - t0) * 1000}ms')
        val = int.from_bytes(bytes, 'little', signed=True) / 1000.0
        shared_arr[idx] = val

    async def activateHW(self):
        await self.client.write_gatt_char(START_CHAR_UUID, bytearray([1]))

async def main():
    controller = BLEController()
    if await controller.connect():
        while True:
            await controller.read_gyro()
    else:
        print("could not connect!")

async def mainShared(x_arr, y_arr, z_arr):
    controller = BLEController()
    if await controller.connect():
        idx = 0
        while True:
            await controller.read_into_mem(x_arr, Axis.X, idx)
            await controller.read_into_mem(y_arr, Axis.Y, idx)
            await controller.read_into_mem(z_arr, Axis.Z, idx)
            idx = (idx + 1) % WINDOW_WIDTH
    else:
        print("could not connect!")

async def mainClock(t):
    controller = BLEController()
    if await controller.connect():
        while True:
            t.value = await controller.read_clock()
    else:
        print("could not connect!")

async def mainAll(orientation, t, direction, wire):
    controller = BLEController()
    if await controller.connect():
        await controller.activateHW()
        while True:
            orientation.value = await controller.read_char(ORIENTATION_CHAR_UUID)
            t.value = await controller.read_char(TIME_CHAR_UUID)
            direction.value = await controller.read_char(DIRECTION_CHAR_UUID)
            wire.value = await controller.read_char(WIRE_CHAR_UUID)
            print("orientation: " + str(orientation.value))
            print("time: " + str(t.value))
            print("direction: " + str(direction.value))
            print("wire cut: "  + str(wire.value))

def runner(orientation, t, direction, wire):
    asyncio.run(mainAll(orientation, t, direction, wire))

if __name__ == '__main__':
    orientation = Value('i', 0)
    t = Value('i', 0)
    direction = Value('i', 0)
    wire = Value('i', 0)
    p = Process(target=runner, args=(orientation, t, direction, wire))
    p.start()
    p.join()
