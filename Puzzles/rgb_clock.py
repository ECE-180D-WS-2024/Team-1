
def check_answer(time, color, freq):
    lastDig = time % 10
    tensDig = ((time // 10)  % 6) % 10
    minsDig = time // 60
    print(lastDig)
    print(tensDig)
    print(minsDig)
    if (color == 5):
        if (lastDig % 5 == 0):
            return True
        else:
            return False
    elif (color == 4 and freq == 1):
        if (lastDig == 1):
            return True
        else:
            return False
    elif (color == 4):
        if (lastDig == 2 or lastDig == 3 or lastDig == 5 or lastDig == 7):
            return True
        else:
            return False
    elif (color == 3 and freq == 0):
        if (lastDig > tensDig):
            return True
        else:
            return False
    elif (color == 3):
        if lastDig % 2 == 0:
            return True
        else:
            return False
    elif (color == 2):
        if (minsDig == 0 or tensDig == 0 or lastDig == 0):
            return True
        else:
            return False
    elif (color == 1 and freq == 2):
        if (tensDig == 2):
            return True
        else:
            return False
    elif (color == 1):
        if (lastDig == 4):
            return True
        else:
            return False
    elif (color == 0):
        if (lastDig == 1 and tensDig == 1):
            return True
        else:
            return False

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
    pass
    
def game_loop(mistakes, **kwargs):
    last_choice = 0
    # Main game loop
    while(True):

        #Check if time ran out
        if (kwargs['time'].value == 0):
            return False
        
        # Prompt the user to press the rgb
        print("Press the RGB button down and don't let go!")
        print("Note it's color and rate of flashing")

        # Wait for button press
        while(kwargs['rgb'].value == 0):
            if kwargs['time'].value == 0:
                return False

        while(kwargs['rgb'].value == 1):
            if kwargs['time'].value == 0:
                return False
        
        # Check if correct release time
        result = check_answer(kwargs['time'].value, kwargs['rgb_color'], kwargs['rgb_freq'])

        # Check result
        if result:
            return True
        else:
            mistakes[0] += 3
            print('Wrong, EXPLODDDINGGGGGGGG')
            # Check if the player has made too many mistakes
            if mistakes[0] >= 3:
                return False


def start_rgb_clock(mistakes, **kwargs):
    return game_loop(mistakes, **kwargs)