import wire_example
import sequence_example
from Tutorial_Utilities.Orientation import Orientation
from Tutorial_Utilities.ble_imu_decode import ble_imu_decode

def main():
    wire_example.init()

    while True:
        print("Starting the bomb defusal tutorial!")
        print("Please enter 's' to start or 'q' to quit :(")
        start = input()
        if start == 's':
            break
        elif start == 'q':
            return
        else:
            print('Unrecognized, please try again.')
            print()
            print()

    while True:
        switch_condition = sequence_example.start_sequence()
        if switch_condition:
            print()
            print(f"Switching puzzle due to switch.")
            print()
            print("Lay bomb flat for 3 seconds, then hit enter to switch to the wires puzzle")
            input() # Wait for input to check orientation

            orientation = ble_imu_decode() # Decode orientation
            if orientation == Orientation.FLAT:
                wire_example.start_wires
                sequence_example.start_sequence()
                break
            else:
                print("Unrecognized orientation, current puzzle will remain active.")
        else:
            print('Nice work, moving to wires.')
            wire_example.start_wires
            break

if __name__ == "__main__":
    main()