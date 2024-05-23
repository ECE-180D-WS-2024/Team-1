import random

from puzzles import Puzzle

from direct.interval.IntervalGlobal import Sequence, Wait, Func

COLOR_MAP = {
    0: 'red',
    1: 'green',
    2: 'blue',
    3: 'yellow',
    4: 'purple',
    5: 'white'
}

light_sequence = None
default_tex = None
color_tex = None

def check_answer(time, color, freq):
    lastDig = time % 10
    tensDig = ((time // 10)  % 6) % 10
    minsDig = time // 60
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

def init(app):
    global light_sequence
    global default_tex
    global color_tex
    global color_num
    global freq

    color_num = random.randint(0, 5) # Color Sent to the bomb: 0 red, 1 green, 2 blue, 3 yellow, 4 purple, 5 white
    freq = random.randint(0, 2) # Flash freq sent to the bomb: 0 none, 1 fast, 2 slow

    light_np = app.bomb.find("**/hold.light")
    default_tex = app.loader.loadTexture("assets/texture/hold_black.png")
    light_np.setTexture(default_tex)

    color_tex_path = f'assets/texture/hold_{COLOR_MAP[color_num]}.png'
    color_tex = app.loader.loadTexture(color_tex_path)

    match freq:
        case 0:
            # Use None as a sentinal value for button handler; if none, button handler
            # should only set the texture instead of looping the sequence
            light_sequence = None
        case 1:
            light_sequence = Sequence(
                Func(light_np.setTexture, color_tex),
                Wait(0.15),
                Func(light_np.setTexture, default_tex),
                Wait(0.15)
            )
        case 2:
            light_sequence = Sequence(
                Func(light_np.setTexture, color_tex),
                Wait(1),
                Func(light_np.setTexture, default_tex),
                Wait(1)
            )

    # rgb_encoding = color_num * 10 + freq
    # return rgb_encoding

def focus(app):
    app.bomb.hprInterval(0.25, (0, 90, 0)).start()
    app.focused = Puzzle.HOLD

def push_button(app):
    hold_button = app.bomb.find('**/hold.btn')
    # Magic numbers are from button_np.ls(); they're the original position
    hold_button.posInterval(0.25, (0.011577, -0.463809, 0.506159)).start()
    if light_sequence is not None:
        light_sequence.loop()
    else:
        light_np = app.bomb.find('**/hold.light')
        light_np.setTexture(color_tex)

def release_button(app):
    hold_button = app.bomb.find('**/hold.btn')
    # Magic numbers are from button_np.ls(); they're the original position
    hold_button.posInterval(0.25, (0.011577, -0.463809, 0.606159)).start()
    if light_sequence is not None:
        light_sequence.finish()
    else:
        light_np = app.bomb.find('**/hold.light')
        light_np.setTexture(default_tex)

    if not app.is_solved(Puzzle.HOLD):
        correct = check_answer(app.secs_remain, color_num, freq)
        if correct:
            app.solve_puzzle(Puzzle.HOLD)
        else:
            app.handle_mistake()
