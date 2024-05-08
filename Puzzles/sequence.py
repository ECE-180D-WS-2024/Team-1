import random
import copy

# Define the manual with sequences for each row
MANUAL = [ 
    ['u', 'l', 'o', 'x', 's', 'd', 'v', 'b'],
    ['j', 't', 'w', 'v', 'h', 'z', 'p', 'y'],
    ['i', 'x', 'q', 'y', 'm', 'g', 'j', 't'],
    ['i', 'c', 'r', 'a', 'm', 'j', 'h', 'd'],
    ['r', 'y', 'c', 'e', 's', 'w', 'i', 'g']
]

key = []
row_n = -1
correct_answer = []

def sequence(answer, key):
    """Check if the answer matches the key in sequence."""
    answer_index = 0  # Index to track position in the answer string
    for char in key:
        if answer_index < len(answer) and char == answer[answer_index]:
            answer_index += 1  # Move to the next character in the answer
        if answer_index == len(answer):  # Found the entire answer in order
            return True
    return False  # Did not find the answer in order


def init():
    global row_n
    global key
    global correct_answer

    row_n = random.randint(0, 4)  # Randomly select a row from the manual
    row = copy.deepcopy(MANUAL[row_n])  # Deep copy the selected row
    random.shuffle(row)  # Shuffle the row to create a key
    key = row[:4]  # Take the first 4 characters as the key
    for i in range(len(MANUAL[row_n]) - 1, -1, -1): # Generate correct_answer as order characters appear right to left
        if MANUAL[row_n][i] in key:
            correct_answer.append(MANUAL[row_n][i])

def game_loop(mistakes, **kwargs):
    global correct_answer
    last_choice = 0
    # Main game loop
    while True:
        answer = ""
        #Check if time ran out
        if (kwargs['time'].value == 0):
            return False
        
        # Present the player with the shuffled key
        print('The bomb shows 4 characters: ', key[0], key[1], key[2], key[3])
        print("Your input to defuse this stage? ('s' to switch puzzles): ")
        while len(answer) < 4:
            # Wait for button press
            while(kwargs['seq'].value == last_choice or kwargs['seq'].value == 0):
                if kwargs['skip'].value == 1 or kwargs['time'].value == 0:
                    return False
            answer += (key[kwargs['seq'].value - 1])
            print(answer)
            last_choice = kwargs['seq'].value
            
        if answer == 's':
            return False

        # Check if the answer matches the reversed row in the manual
        if sequence(answer, correct_answer):
            return True
        else:
            mistakes[0] += 1
            print('Wrong, Mistakes: ', mistakes[0])
            # Check if the player has made too many mistakes
            if mistakes[0] >= 3:
                return False


def start_sequence(mistakes, **kwargs):
    return game_loop(mistakes, **kwargs)