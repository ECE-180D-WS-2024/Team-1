import readline

def game_loop():
    while True:
        print("Get instructions from the bomb manual player on what sequence to press the buttons in, then press the buttons accordingly (WASD)")
        user_choice = input("Your input to defuse this stage?\n")

        correct_sequence = "adws"
        # Compare user input with correct wire
        if user_choice == correct_sequence:
            print("Correct!")
            return True
        else:
            print('Wrong, try again!')

def start_sequence():
    return game_loop()