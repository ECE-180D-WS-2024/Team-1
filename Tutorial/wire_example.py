import random

wires = ['r', 'b', 'g']

def init():
    global wires
    random.shuffle(wires) 
    
def game_loop():
    # Main game loop
    while(True):
        # Print the wire sequence and color legend
        print(f"There are 3 wires: {''.join(wires)}")
        print(f"Get instructions from the bomb defusal player on what wire to cut, then enter the keyboard number that corresponds to that wire (1-indexed).")
            
        # Wait for button press
        user_choice = input("Your input to defuse this stage?\n")
        correct_wire = wires.index('r') + 1

        # Compare user input with correct wire
        if int(user_choice) == correct_wire:
            print("Correct!")
            return True
        else:
            print('Wrong, try again!')


def start_wires():
    return game_loop()

