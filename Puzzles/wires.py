import random

clue = 'b'  # The initial clue for the player
mistake = 0  # Initialize mistake counter

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

# Generate a random sequence of 6 wires, add a black wire, and a random number L
colors = ['r', 'y', 'b', 'g', 'w', 'o']  # Example colors: red, yellow, blue, green, white, orange
wires = random.choices(colors, k=5)  # Choose 5 wires randomly
wires.append('k')  # Add a black wire
random.shuffle(wires)  # Shuffle the wires to mix the black wire randomly
L = random.randint(1, 9)  # Random number L between 1 and 9

# Main game loop
while(True):
    # Print the wire sequence and color legend
    print(f"There are 6 wires: {''.join(wires)}")
    print(f"The bomb shows a number: {L}")

    # Prompt the user for input
    print("Your input to defuse this stage?: ")
    user_choice = int(input())

    # Determine the correct wire to cut
    correct_wire = decide_wire_to_cut(wires, L)

    # Compare user input with correct wire
    if user_choice == correct_wire:
        print('Congrats: that was correct.')
        print('Here is your next clue: ', clue)
        print('Switching to next game.')
        break
    else:
        mistake += 1
        print('Wrong, Mistakes: ', mistake)
        # Check if the player has made too many mistakes
        if mistake >= 3:
            print('BOOOOOOOM, BOMB HAS EXPLODED, YOU LOSE.')
            break
        else:
            print('Please Retry')
