import random
import copy

# Define the manual with sequences for each row
manual = [ 
    ['u', 'l', 'o', 'x', 's', 'd', 'v', 'b'],
    ['j', 't', 'w', 'v', 'h', 'z', 'p', 'y'],
    ['i', 'x', 'q', 'y', 'm', 'g', 'j', 't'],
    ['i', 'c', 'r', 'a', 'm', 'j', 'h', 'd'],
    ['r', 'y', 'c', 'e', 's', 'w', 'i', 'g']
]

mistake = 0  # Counter for mistakes made by the player
clue = 'a'  # Initial clue for the player

def sequence(answer, key):
    """Check if the answer matches the key in sequence."""
    answer_index = 0  # Index to track position in the answer string
    for char in key:
        if answer_index < len(answer) and char == answer[answer_index]:
            answer_index += 1  # Move to the next character in the answer
        if answer_index == len(answer):  # Found the entire answer in order
            return True
    return False  # Did not find the answer in order

row_n = random.randint(0, 4)  # Randomly select a row from the manual
row = copy.deepcopy(manual[row_n])  # Deep copy the selected row
random.shuffle(row)  # Shuffle the row to create a key
key = row[:4]  # Take the first 4 characters as the key

# Main game loop
while True:
    # Present the player with the shuffled key
    print('The bomb shows 4 characters: ', key[0], key[1], key[2], key[3])
    print("Your input to defuse this stage?: ")
    answer = input()

    # Check if the answer matches the reversed row in the manual
    if sequence(answer, manual[row_n][::-1]):
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
