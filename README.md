# Team-1
Team members:
Nicholas Nhien, Matthew Fiorella, Krish Shah, Nicholas Hamakami

Our game is a physical implementation of the popular game, Keep Talking and Nobody Explodes.
In this game, two players work together to defuse a bomb.
Player 1 is the instructing player, who has a manual of the bomb, but cannot see the individual bomb components.
Player 2 is the defusing player, who has access to the bomb's components and inputs, but cannot see instructions on what to do in order to defuse the bomb.
The players must communicate without looking at each other's screens in order to diffuse the bomb.

Although we don't have a physical version of the bomb or GUI at this time, our current repository contains a working CLI version of the game.

Instructions on playing the game:

1. Have the defusing player run the command:
$sh PlayGame.sh

2. Have the instructing player open the instruction manual PDF.

3. As the defusing player, switch the orientation of the Nano33IOT Arduino to select a puzzle.

4. Complete all the puzzles by communicating together (without looking at each other's screens), while making less than 3 mistakes to win the game!