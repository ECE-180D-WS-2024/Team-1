import random

wires = []
L = -1

COLORS = ['r', 'y', 'b', 'g', 'w', 'o', 'k']  # Example colors: red, yellow, blue, green, white, orange, black


def decide_wire_to_cut(wires, L):
    # Count the number of each color of wire
    yellow_count = wires.count('y')
    white_count = wires.count('w')
    red_count = wires.count('r')

    # Decision logic to determine which wire to cut based on the given conditions
    if yellow_count == 0 and L % 2 != 0:
        return 3  # Cut the third wire
    elif yellow_count == 1 and white_count > 1:
        return 4  # Cut the fourth wire
    elif red_count == 0:
        return 6  # Cut the last wire
    else:
        return 4  # Otherwise, cut the fourth wire
    

def init():
    global wires
    global L
    
    # Generate a random sequence of 6 wires, add a black wire, and a random number L
    wires = random.choices(COLORS, k=6)  # Choose 6 wires randomly
    random.shuffle(wires)  # Shuffle the wires to mix the black wire randomly
    L = random.randint(1, 9)  # Random number L between 1 and 9
    
def game_loop(mistakes):

    # Main game loop
    while(True):
        # Print the wire sequence and color legend
        print(f"There are 6 wires: {''.join(wires)}")
        print(f"The bomb shows a number: {L}")

        # Prompt the user for input
        print("Your input to defuse this stage? ('s' to switch puzzles): ")
        user_choice = input()

        if user_choice == 's':
            return False

        # Determine the correct wire to cut
        correct_wire = decide_wire_to_cut(wires, L)

        # Compare user input with correct wire
        if int(user_choice) == correct_wire:
            return True
        else:
            mistakes[0] += 1
            print('Wrong, Mistakes: ', mistakes[0])
            # Check if the player has made too many mistakes
            if mistakes[0] >= 3:
                return False


def start_wires(mistakes):
    return game_loop(mistakes)