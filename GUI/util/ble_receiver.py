from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice
from enum import Enum, auto
from multiprocessing import Value

import random
import asyncio
import random

from .decode import ble_imu_decode, ble_wires_decode, ble_rgb_decode, ble_sequence_decode
from . import event
from .RGB import RGB
from .Orientation import Orientation
from .Sequence import Sequence
from .Wires import Wire

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
        attempts = 0
        while device is None and attempts < 3:
            device = await BleakScanner.find_device_by_name(self.device_name, timeout=5)
            if device is None:
                attempts += 1
        return device

    async def connect(self) -> bool:
        # Discover device
        self.device: BLEDevice = await self.discover()
        if self.device is None:
            return False

        # Create client
        self.client: BleakClient = BleakClient(self.device)
        return await self.client.connect()

    async def disconnect(self):
        await self.client.disconnect()

    async def read_char(self, char_uuid: str) -> int:
        bytes = await self.client.read_gatt_char(char_uuid)
        val = int.from_bytes(bytes, "little", signed=True)
        return val

    async def activateHW(self):
        await self.client.write_gatt_char(START_CHAR_UUID, bytearray([1]))

    async def configRGB(self, encode_rgb: int):
        await self.client.write_gatt_char(RGB_CHAR_UUID, bytearray([encode_rgb]))


async def mainAll(app, orientation, t, sequence, wire, rgb, rgb_encoding):
    controller = BLEController()

    if await controller.connect():
        await controller.activateHW()
        await controller.configRGB(rgb_encoding)
        while True:
            if not app.running:
                break
            orientation.value = await controller.read_char(ORIENTATION_CHAR_UUID)
            t.value = await controller.read_char(TIME_CHAR_UUID)
            sequence.value = await controller.read_char(SEQUENCE_CHAR_UUID)
            wire.value = await controller.read_char(WIRE_CHAR_UUID)
            rgb.value = await controller.read_char(RGB_PRESSED_CHAR_UUID)
        await controller.disconnect()

def runner(app, orientation, t, sequence, wire, rgb, rgb_encoding):
    asyncio.run(mainAll(app, orientation, t, sequence, wire, rgb, rgb_encoding))

"""
    Allocates memory and begins the communications loop
"""
def spawn(app, rgb_encoding):
    orientation = Value('i', 0) # Use to get Orientation
    time = Value('i', 0) # Use to get time value in seconds
    seq = Value('i', 0) # Use to get Sequence Selection
    wire = Value('i', 0) # Use to get Wire Selection
    rgb = Value('i', 0)

    state_dict = {
        'orientation': Orientation.OTHER,
        'time': 0,
        'sequence': Sequence.NO_PRESS,
        'wire': Wire.NO_PRESS,
        'rgb': RGB.NOT_PRESSED
    }

    app.taskMgr.setupTaskChain('message_bus', numThreads=1)
    app.taskMgr.setupTaskChain('ble_receiver', numThreads=1)

    app.taskMgr.add(task_check_data, extraArgs=[app, state_dict, orientation, time, seq, wire, rgb], appendTask=True, taskChain='message_bus')
    app.taskMgr.add(runner, extraArgs=[app, orientation, time, seq, wire, rgb, rgb_encoding], taskChain='ble_receiver')

def poll_button_and_handle_message(messenger, state_dict, key, ble_value, decode_fn):
    if ble_value.value != 0:
        if state_dict[key] is None:
            decoded = decode_fn(ble_value.value)
            payload = event.encode(key, decoded)
            messenger.send(payload)
            state_dict[key] = decoded
    else:
        state_dict[key] = None


def task_check_data(app, prev_values, orientation, t, sequence, wire, rgb, task):
    if not app.running:
        return task.done

    # Use time decrement as heartbeat
    if prev_values['time'] != t.value:
        app.messenger.send('heartbeat', sentArgs=[t.value])
        prev_values['time'] = t.value
    
    decoded_orientation = ble_imu_decode(orientation.value)
    if prev_values['orientation'] != decoded_orientation:
        app.messenger.send(event.encode('orientation', decoded_orientation))
        prev_values['orientation'] = decoded_orientation

    poll_button_and_handle_message(app.messenger, prev_values, 'sequence', sequence, ble_sequence_decode)
    poll_button_and_handle_message(app.messenger, prev_values, 'wire', wire, ble_wires_decode)

    decoded_rgb = ble_rgb_decode(rgb.value)
    if prev_values['rgb'] != decoded_rgb:
        app.messenger.send(event.encode('rgb', decoded_rgb))
        prev_values['rgb'] = decoded_rgb

    return task.again
