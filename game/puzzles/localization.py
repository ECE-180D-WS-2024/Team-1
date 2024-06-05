import numpy as np
import cv2
import random

from puzzles import Puzzle

from panda3d.core import PointLight
from direct.task import Task

from direct.interval.IntervalGlobal import Sequence, Func, Wait

# Constants for the game
MARGIN_H = 12
MARGIN_S = 18
MARGIN_V = 18

MAX_FLASHES = 1
STAGE_COUNT = 4
COLORS = ['r','g','y','b']
COLOR_REPEAT_CORNER_CONVERSION_TABLE = {
    'r': {1: 4, 2: 4, 3: 2},
    'g': {1: 2, 2: 4, 3: 2},
    'y': {1: 1, 2: 1, 3: 3},
    'b': {1: 3, 2: 1, 3: 3}
}

stages = []
curr_stage = 0
answer_key = []
curr_sequence = None
lower_limit = np.array([])
upper_limit = np.array([])

def generate_stages():
    """Generate a sequence of colors (stages) for the game."""
    stages_local = []
    order = random.sample([0, 1, 2, 3], 4)
    for i in range(STAGE_COUNT):
        l_color = [COLORS[order[i]]] * random.randint(1, MAX_FLASHES) # Random color, random repeats
        s_color = ''.join(l_color)
        stages_local.append(s_color)
    return stages_local

def generate_key(stages):
    """Generate the solution key based on the stages."""
    answer_key_local = []
    for pattern in stages:
        answer_key_local.append(COLOR_REPEAT_CORNER_CONVERSION_TABLE[pattern[0]][len(pattern)])
    return answer_key_local

def init(app, color):
    global np_state
    global lower_limit
    global upper_limit


    def setup_light(color_str, color_vec):
        ss_sphere_np = app.bomb.find(f"**/ss.{color_str}")
        sphere_light_node = PointLight(f"ss.{color_str}_light")
        sphere_light_node.setColor(color_vec)

        sphere_light_np = ss_sphere_np.attachNewNode(sphere_light_node)
        sphere_light_np.setPos(0, 0, 0.5)

        return (ss_sphere_np, sphere_light_np)

    ss_red_nps = setup_light('red', (255, 0, 0, 0))
    ss_green_nps = setup_light('green', (0, 255, 0, 0))
    ss_blue_nps = setup_light('blue', (0, 0, 255, 0))
    ss_yellow_nps = setup_light('yellow', (255, 255, 0, 0))

    np_state = {}
    np_state['r'] = (*ss_red_nps, False)
    np_state['g'] = (*ss_green_nps, False)
    np_state['b'] = (*ss_blue_nps, False)
    np_state['y'] = (*ss_yellow_nps, False)

    lower_limit = np.array([color[0] - MARGIN_H, color[1] - MARGIN_S, color[2] - MARGIN_V])
    upper_limit = np.array([color[0] + MARGIN_H, color[1] + MARGIN_S, color[2] + MARGIN_V])

    generate_puzzle()
    

def generate_puzzle():
    global stages
    global curr_stage
    global curr_sequence
    global answer_key

    if curr_sequence is not None:
        curr_sequence.finish()

    # Generate game stages and solution key
    stages = generate_stages()
    curr_stage = 0
    answer_key = generate_key(stages)

    stage0_interval = __generate_stage_sequence(0)
    curr_sequence = Sequence(stage0_interval, Wait(1.5))
    curr_sequence.loop()

def __enable_ss_light(color_str):
    (ss_sphere_np, sphere_light_np, _) = np_state[color_str]
    ss_sphere_np.setLight(sphere_light_np)

def __disable_ss_light(color_str):
    (ss_sphere_np, sphere_light_np, _) = np_state[color_str]
    ss_sphere_np.setLightOff(sphere_light_np)

def __generate_stage_sequence(stage_num):
    color = stages[stage_num][0]
    repeats = stages[stage_num].count(color)

    seq = Sequence()
    seq.append(Func(__enable_ss_light, color))
    seq.append(Wait(0.25))
    seq.append(Func(__disable_ss_light, color))
    for _ in range(repeats - 1):
        seq.append(Wait(0.4))
        seq.append(Func(__enable_ss_light, color))
        seq.append(Wait(0.25))
        seq.append(Func(__disable_ss_light, color))

    return seq

def __correct_answer(answer, stage):
    return answer == answer_key[stage]

def __end_of_stage(user_answers):
    return len(user_answers) == curr_stage + 1

def focus(app):
    app.bomb.hprInterval(0.25, (180, 0, 0)).start()
    app.focused = Puzzle.LOCALIZATION
    print(answer_key)

    if not app.is_solved(Puzzle.LOCALIZATION):
        # Initialize game variables
        # Set up video capture
        cap = cv2.VideoCapture(0)  # Start video capture
        while not cap.isOpened():
            pass
        BORDER_THICKNESS = 50
        width = int(cap.get(3)) + 2*BORDER_THICKNESS  # Get video width
        height = int(cap.get(4)) + 2*BORDER_THICKNESS  # Get video height
        # Define screen boundary constants for bomb movement
        bounds = {
            "ly": int(width/4),
            "rx": int(3*width/4),
            "ty": int(height/3),
            "by": int(2*height/3),
        }

        print(bounds)

        dimens = {
            "width": width,
            "height": height,
            "margin_x": int(width/8)
        }

        task_state = {
            "app": app,
            "cap": cap,
            "BORDER_THICKNESS": BORDER_THICKNESS,
            "bounds": bounds,
            "dimens": dimens,
            "user_answers": [],
            "new_added": False,
            "centered": False
        }

        # Game loop for each stage
        app.taskMgr.add(task_process_cv_frame, "process_cv_frame", extraArgs=[task_state], appendTask=True)

def task_process_cv_frame(task_state, task: Task):
    app = task_state["app"]
    cap = task_state["cap"]
    border_thickness = task_state["BORDER_THICKNESS"]
    bounds = task_state["bounds"]
    dimens = task_state["dimens"]

    width = dimens["width"]
    height = dimens["height"]
    margin_x = dimens["margin_x"]

    if app.focused != Puzzle.LOCALIZATION or not app.running:
        cv2.destroyAllWindows()
        cap.release()
        return task.done

    global curr_stage
    global curr_sequence

    _, image = cap.read()
    image = cv2.flip(image, 1) # Flip the image for natural interaction
    image = cv2.copyMakeBorder(image, border_thickness, border_thickness, border_thickness, border_thickness, cv2.BORDER_CONSTANT, value=(255, 255, 255))

    # convert from BGR to HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Create a mask to detect objects within the color range
    mask = cv2.inRange(hsv_image, lower_limit, upper_limit)
    contours, _ = cv2.findContours(mask, 1, 2) # Find contours in the mask

    # Draw rectangles to indicate different zones on the screen
    cv2.rectangle(image, (0, 0), (bounds["ly"], bounds["ty"]), (0, 0, 255),  4)
    cv2.rectangle(image, (bounds["rx"], 0), (width, bounds["ty"]), (0, 0, 255), 4)
    cv2.rectangle(image, (0, bounds["by"]), (bounds["ly"], height), (0, 0, 255), 4)
    cv2.rectangle(image, (bounds["rx"], bounds["by"]), (width, height), (0, 0, 255), 4)
    # Center rectangle
    cv2.rectangle(image, (bounds["ly"] + margin_x, bounds["ty"]), \
                (bounds["rx"]-margin_x, bounds["by"]), (0, 255, 0), 4)

    # Process the largest contour detected
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour) # Get bounding box of largest contour
        cv2.rectangle(image, (x + int(w/2) - 2, y + int(h/2) - 2), (x + int(w/2) + 2, y + int(h/2) + 2), (255, 0, 0), 4) # Draw bounding box

        color_middle_x = x + w/2
        color_middle_y = y + h/2

        # Check if the object is centered within the designated area
        if color_middle_x <= bounds["rx"] - margin_x and color_middle_x >= bounds["ly"] + margin_x and \
            color_middle_y >= bounds["ty"] and color_middle_y <= bounds["by"]:
            task_state["centered"] = True
        
        # Check the corner based on object position and add user's answer
        if task_state["centered"]:
            if color_middle_x < bounds["ly"] and color_middle_y < bounds["ty"]:
                task_state["user_answers"].append(1)
                task_state["new_added"] = True
                task_state["centered"] = False
            elif color_middle_x > bounds["rx"] and color_middle_y < bounds["ty"]:
                task_state["user_answers"].append(2)
                task_state["new_added"] = True
                task_state["centered"] = False
            elif color_middle_x < bounds["ly"] and color_middle_y > bounds["by"]:
                task_state["user_answers"].append(3)
                task_state["new_added"] = True
                task_state["centered"] = False
            elif color_middle_x > bounds["rx"] and color_middle_y > bounds["by"]:
                task_state["user_answers"].append(4)
                task_state["new_added"] = True
                task_state["centered"] = False
            
        # Validate user's answer with the answer key
        if task_state["new_added"]:
            task_state["new_added"] = False
            if __correct_answer(answer = task_state["user_answers"][-1], stage=len(task_state["user_answers"]) - 1):

                """
                    if at final required corner for this stage:
                        advance to next stage
                    else:
                        go to next loop iteration

                    advance to next stage:
                        reset user_answer array
                        increment curr_stage pointer
                        add next stage's sequence to light sequence
                """

                print(curr_stage + 1)
                if __end_of_stage(task_state["user_answers"]):
                    task_state["user_answers"] = []

                    # Check if the game will be completed
                    if curr_stage + 1 == STAGE_COUNT:
                        curr_sequence.finish()
                        app.solve_puzzle(Puzzle.LOCALIZATION)
                    else:
                        next_stage_sequence = __generate_stage_sequence(curr_stage + 1)
                        curr_sequence.finish()

                        curr_sequence = Sequence(curr_sequence, next_stage_sequence, Wait(1.5))
                        curr_sequence.loop()
                        
                        curr_stage += 1
                        app.sound_success.play()
            else:
                app.handle_mistake()
                task_state["user_answers"] = [] # Reset user answer for the current stage

    cv2.imshow("image", image)

    if not app.is_solved(Puzzle.LOCALIZATION):
        return task.again
    else:
        cv2.destroyAllWindows()
        cap.release()
        return task.done
