# import warnings
# warnings.simplefilter("ignore")

import random
from Puzzles import localization, sequence, speech, wires, rgb_clock
from Utilities.Orientation import Orientation
from Utilities.decode import ble_imu_decode
from Utilities.color_calibration import calibrate
from multiprocessing import Process, Value
from GUI.util.ble_receiver import runner, configRunner
import numpy as np
import os
# Mistake threshold
THRESHOLD = 3
# Number of IMU readings averaged
IMU_WINDOW = 10

# Initialize the game state
PUZZLES = {
    'wires': wires.start_wires,
    'localization': localization.start_localization,
    'sequence': sequence.start_sequence,
    'speech': speech.start_speech,
    'rgb_clock': rgb_clock.start_rgb_clock
}


def main():
    # Initialize shared memory
    orientation = Value('i', 0) # Use to get Orientation
    time = Value('i', 0) # Use to get time value in seconds
    seq = Value('i', 0) # Use to get Sequence Selection
    wire = Value('i', 0) # Use to get Wire Selection
    skip = Value('i', 0)
    words = Value('i', 0)
    rgb = Value('i', 0)
    color = random.randint(0, 5) # Color Sent to the bomb: 0 red, 1 green, 2 blue, 3 yellow, 4 purple, 5 white
    freq = random.randint(0, 2) # Flash freq sent to the bomb: 0 none, 1 fast, 2 slow
    encode_rgb = color * 10 + freq
    p_config = Process(target=configRunner, args=[encode_rgb])
    p_config.start()
    p_config.join()
    p = Process(target=runner, args=(orientation, time, seq, wire, skip, words, rgb))
    p.start()

    wires.init()
    localization.init(calibrate())
    sequence.init()
    speech.init()

    os.system('clear')
    while True:
        print("Welcome to the Bomb Defusal Game!")
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
            
    completed_games = set()
    mistakes = [0]  # Use a list to simulate pass by reference
    last_game = None
    switch_condition = False # Tracks if game state is being switched
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

        if switch_condition: # If user requests to switch game prompt orientations to select
            for game in remaining_games: # Print orientations for remaining games
                if game == "wires":
                    print("Lay bomb flat to switch to the wires puzzle")
                elif game == "localization":
                    print("Turn bomb upside down to switch to the localization puzzle")
                elif game == "sequence":
                    print("Orient the antenna up to switch to the sequencing puzzle")
                elif game == "speech":
                    print("Orient the antenna down to switch to the speech puzzle")
            
            print("Hold bomb in desired position for 3 seconds and press enter to switch the puzzle")
            input() # Wait for input to check orientation

            orientation_val = ble_imu_decode(orientation.value) # Decode orientation
            if orientation_val == Orientation.FLAT and 'wires' in remaining_games:
                game_key = 'wires'
            elif orientation_val == Orientation.UPSIDE_DOWN and  'localization' in remaining_games:
                game_key = 'localization'
            elif orientation_val == Orientation.ANTENNA_UP and 'sequence' in remaining_games:
                game_key = 'sequence'
            elif orientation_val == Orientation.ANTENNA_DOWN and 'speech' in remaining_games:
                game_key = 'speech'
            else:
                print("unrecognized orientation, current puzzle will remain active")
                game_key = last_game

        game_func = PUZZLES[game_key]
        switch_condition = False
        print(f"\nStarting Puzzle...")
        success = game_func(mistakes, time=time, wire=wire, seq=seq, skip=skip, speech=words, rgb_color=color, rgb_freq=freq, rgb=rgb)
        
        if success:
            print("Puzzle Completed Successfully!")
            completed_games.add(game_key)
            last_game = None  # Reset last game since this game was successful
        else:
            if mistakes[0] >= THRESHOLD or time.value == 0:
                print()
                print()
                print("BOMB GOES BOOOOOOOOOOOOM, YOU LOSE!")
                print()
                print()
                p.terminate()
                return  # End the game immediately
            else:
                print()
                print(f"Switching puzzle due to switch. Current mistakes: {mistakes[0]}")
                print()
                last_game = game_key  # Set this game as the last game played
                switch_condition = True
                
    if len(completed_games) == len(PUZZLES):
        print("Congratulations! You've successfully defused the bomb by completing all puzzles!")
        p.terminate()

if __name__ == "__main__":
    main()
