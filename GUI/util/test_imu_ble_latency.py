import sys, os, asyncio
sys.path.append(os.path.abspath('..'))
from BLE_Module.BLE_Writer import asyncMainTestTiming


if __name__ == "__main__":
    # Run as async
    asyncio.run(asyncMainTestTiming())   