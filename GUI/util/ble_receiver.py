from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice
from enum import Enum, auto
from multiprocessing import Value
import struct
import math
import time
import random
import asyncio

from direct.showbase.Messenger import Messenger
from .decode import ble_imu_decode

X_ACCEL_CHAR_UUID = "663fdcf8-2126-464d-a6c1-c882f5477fb7"
Y_ACCEL_CHAR_UUID = "e6ac0344-9aee-49ab-b601-1d26b77cf08c"
Z_ACCEL_CHAR_UUID = "224ad21b-9c75-4e1c-a3f0-51c0c7d0a9a8"
X_ANGULAR_VELO_CHAR_UUID = "4de63bcd-e713-4e28-9392-3cc1d7efbabc"
Y_ANGULAR_VELO_CHAR_UUID = "99c07d47-9018-489b-a937-0d911a61aa69"
Z_ANGULAR_VELO_CHAR_UUID = "85c17e72-fb28-4883-9333-479b20fce5a7"


ORIENTATION_CHAR_UUID = "ba90a02e-9acd-4f6b-8d2d-db52abdab1ab"
SEQUENCE_CHAR_UUID = "2e1c9e14-a3d6-41d6-a484-114375527aa6"
WIRE_CHAR_UUID = "5101a8d5-e8da-4ef6-9e03-1c0573d25429"
TIME_CHAR_UUID = "2e92fbab-6365-4ce6-aa19-9b1fe217888c"
START_CHAR_UUID = "d1b05699-f934-43e3-ae5f-2510118995f7"
SKIP_CHAR_UUID = "31a276d9-606a-4089-971f-0c3c349a7374"
SPEECH_CHAR_UUID = "068891ec-d3b6-4d8a-9572-d4292b02e729"
RGB_CHAR_UUID = "5976c24b-7bf4-493f-84d6-11c8ca71d899"
RGB_PRESSED_CHAR_UUID = "b12b0137-a6a4-4e6c-b3a2-824e5827afda"

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

    async def configRGB(self, encode_rgb: int):
        await self.client.write_gatt_char(RGB_CHAR_UUID, bytearray([encode_rgb]))

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

async def mainAll(orientation, t, sequence, wire, speech, rgb):
    controller = BLEController()
    print("mainAll")
    if await controller.connect():
        print("connected")
        await controller.activateHW()
        while True:
            orientation.value = await controller.read_char(ORIENTATION_CHAR_UUID)
            t.value = await controller.read_char(TIME_CHAR_UUID)
            sequence.value = await controller.read_char(SEQUENCE_CHAR_UUID)
            wire.value = await controller.read_char(WIRE_CHAR_UUID)
            speech.value = await controller.read_char(SPEECH_CHAR_UUID)
            rgb.value = await controller.read_char(RGB_PRESSED_CHAR_UUID)

async def configRGB(encode_rgb):
    sub_controller = BLEController(device_name="RGB Config")
    if await sub_controller.connect():
        await sub_controller.configRGB(encode_rgb)
        while True:
            ack = await sub_controller.read_char(RGB_CHAR_UUID)
            if ack == -1:
                await sub_controller.client.disconnect()
                return

def runner(orientation, t, sequence, wire, speech, rgb):
    asyncio.run(mainAll(orientation, t, sequence, wire, speech, rgb))

"""
    Allocates memory and begins the communications loop
"""
class InputMessenger(Messenger):
    def __init__(self):
        super().__init__()


def spawn(app):
    orientation = Value('i', 0) # Use to get Orientation
    time = Value('i', 0) # Use to get time value in seconds
    seq = Value('i', 0) # Use to get Sequence Selection
    wire = Value('i', 0) # Use to get Wire Selection
    words = Value('i', 0)
    rgb = Value('i', 0)

    color = random.randint(0, 5) # Color Sent to the bomb: 0 red, 1 green, 2 blue, 3 yellow, 4 purple, 5 white
    freq = random.randint(0, 2) # Flash freq sent to the bomb: 0 none, 1 fast, 2 slow
    encode_rgb = color * 10 + freq

    messenger = InputMessenger()

    state_dict = {
        'orientation': None,
        'time': None,
        'sequence': None,
        'wire': None,
        'words': None,
        'rgb': None
    }

    app.taskMgr.setupTaskChain('message_bus', numThreads=1)
    app.taskMgr.setupTaskChain('ble_receiver', numThreads=1)

    app.taskMgr.add(task_check_data, extraArgs=[messenger, state_dict, orientation, time, seq, wire, words, rgb], appendTask=True, taskChain='message_bus')
    app.taskMgr.add(runner, extraArgs=[orientation, time, seq, wire, words, rgb], taskChain='ble_receiver')

def poll_button_and_handle_message(messenger, state_dict, key, ble_value):
    if ble_value.value != 0:
        if state_dict[key] == None:
            messenger.send(key, sentArgs=[ble_value.value])
            state_dict[key] = ble_value.value
    else:
        state_dict[key] = None


def task_check_data(messenger: InputMessenger, prev_values, orientation, t, sequence, wire, speech, rgb, task):
    print("check_data")
    # Use time decrement as heartbeat
    if prev_values['time'] != t.value:
        messenger.send('heartbeat', sentArgs=[t.value])
        prev_values['time'] = t.value
        print(f'time: {t.value}')
    
    decoded_orientation = ble_imu_decode(orientation)
    if prev_values['orientation'] != decoded_orientation:
        messenger.send('orientation', sentArgs=[decoded_orientation])
        prev_values['orientation'] = decoded_orientation
        print(f'orientation: {decoded_orientation}')

    poll_button_and_handle_message(messenger, prev_values, 'sequence', sequence)
    poll_button_and_handle_message(messenger, prev_values, 'wire', wire)

    return task.again
