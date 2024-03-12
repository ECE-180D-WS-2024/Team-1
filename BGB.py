# import warnings
# warnings.simplefilter("ignore")

import random
from Puzzles import localization, sequence, speech, wires

# Mistake threshold
THRESHOLD = 3

# Initialize the game state
PUZZLES = {
    'wires': wires.start_wires,
    'localization': localization.start_localization,
    'sequence': sequence.start_sequence,
    'speech': speech.start_speech
}


def main():

    wires.init()
    localization.init()
    sequence.init()
    speech.init()

    print()
    print()
    print("Welcome to the Bomb Defusal Game!")
    
    completed_games = set()
    mistakes = [0]  # Use a list to simulate pass by reference
    last_game = None
    
    # Main game loop
    while len(completed_games) < len(PUZZLES):
        # Filter games: completed games and last game (if mistakes are under threshold)
        if last_game:
            remaining_games = list(set(PUZZLES.keys()) - completed_games - {last_game})
        else:
            remaining_games = list(set(PUZZLES.keys()) - completed_games)
        
        if not remaining_games:  # In case last_game is the only remaining game but we can't repeat it immediately
            remaining_games.append(last_game)  # Allow last game if it's the only option left
        
        game_key = random.choice(remaining_games)
        game_func = PUZZLES[game_key]
        
        print(f"\nStarting Puzzle...")
        success = game_func(mistakes)
        
        if success:
            print("Puzzle Completed Successfully!")
            completed_games.add(game_key)
            last_game = None  # Reset last game since this game was successful
        else:
            if mistakes[0] >= THRESHOLD:
                print()
                print()
                print("BOMB GOES BOOOOOOOOOOOOM, YOU LOSE!")
                print()
                print()
                return  # End the game immediately
            else:
                print()
                print(f"Switching puzzle due to switch. Current mistakes: {mistakes[0]}")
                print()
                last_game = game_key  # Set this game as the last game played
                
    if len(completed_games) == len(PUZZLES):
        print("Congratulations! You've successfully defused the bomb by completing all puzzles!")

if __name__ == "__main__":
    main()
