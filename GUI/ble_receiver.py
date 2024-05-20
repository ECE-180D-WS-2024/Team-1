from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice
from enum import Enum, auto
from multiprocessing import Process, Value
import struct
import math
import asyncio
import time
import random


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

    async def read_char(self, char_uuid: str) -> int:
        bytes = await self.client.read_gatt_char(char_uuid)
        val = int.from_bytes(bytes, "little", signed=True)
        return val

    async def activateHW(self):
        await self.client.write_gatt_char(START_CHAR_UUID, bytearray([1]))

    async def configRGB(self, encode_rgb: int):
        await self.client.write_gatt_char(RGB_CHAR_UUID, bytearray([encode_rgb]))


async def mainAll(orientation, t, sequence, wire, rgb):
    color = random.randint(0, 5) # Color Sent to the bomb: 0 red, 1 green, 2 blue, 3 yellow, 4 purple, 5 white
    freq = random.randint(0, 2) # Flash freq sent to the bomb: 0 none, 1 fast, 2 slow
    encode_rgb = color * 10 + freq
    controller = BLEController()
    if await controller.connect():
        await controller.activateHW()
        await controller.configRGB(encode_rgb)
        while True:
            orientation.value = await controller.read_char(ORIENTATION_CHAR_UUID)
            t.value = await controller.read_char(TIME_CHAR_UUID)
            sequence.value = await controller.read_char(SEQUENCE_CHAR_UUID)
            wire.value = await controller.read_char(WIRE_CHAR_UUID)
            rgb.value = await controller.read_char(RGB_PRESSED_CHAR_UUID)
            print("orientation: " + str(orientation.value))
            print("time: " + str(t.value))
            print("sequence: " + str(sequence.value))
            print("wire: " + str(wire.value))
            print("rgb: " + str(rgb.value))
            
def runner(orientation, t, sequence, wire, rgb):
    asyncio.run(mainAll(orientation, t, sequence, wire, rgb))

if __name__ == '__main__':
    orientation = Value('i', 0)
    t = Value('i', 0)
    sequence = Value('i', 0)
    wire = Value('i', 0)
    rgb = Value('i', 0)
    p = Process(target=runner, args=(orientation, t, sequence, wire, rgb))
    p.start()
    p.join()
