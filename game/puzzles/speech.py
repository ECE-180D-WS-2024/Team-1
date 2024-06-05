from enum import Enum, auto

import speech_recognition as sr
import random
from puzzles import Puzzle

from panda3d.core import PointLight

recognizer = None
bytes_hex_str = []
puzzle_bytes = []
word = ''

class Status(Enum):
    LISTENING = auto()
    IDLE = auto()

def generate_code():
    """Generate a code according to the given rules."""
    byte_key = [] # Ordering: 0 -> sequence, 1 -> wires, 2 -> localization, 3 -> hold

    # Generate 4 bytes
    for _ in range(4):
        byte_key.append(random.randint(0, 3))
    bytes_hex_strs = [format(b, '02b') for b in byte_key]

    return byte_key, bytes_hex_strs

def analyze_code(bytes):
    """Analyze the code and determine the output based on the given rules."""
    binary_bytes = [format(b, '02b') for b in bytes]

    # Split the code into individual bytes
    # Check the conditions and determine the output
    print(binary_bytes)
    if binary_bytes[0][0] == '1':
        return "Orange"
    elif int(binary_bytes[1], 2) == 3:
        return "Banana"
    elif binary_bytes[2][-1] == '0':
        return "Apple"
    else:
        return "Dragonfruit"
    
def init(app):
    global recognizer
    global status_nps

    def setup_light(color_str, color_vec):
        status_np = app.bomb.find(f"**/speech.status_{color_str}")
        sphere_light_node = PointLight(f"speech.{color_str}_light")
        sphere_light_node.setColor(color_vec)

        sphere_light_np = status_np.attachNewNode(sphere_light_node)
        sphere_light_np.setPos(0, 0, 0.5)

        return (status_np, sphere_light_np)

    status_nps = {
        'blue': setup_light('blue', (0, 0, 255, 1)),
        'red': setup_light('red', (255, 0, 0, 1))
    }

    __set_status(Status.IDLE)

    # Create task chain to allow speech recognition 
    # to run on a thread separate from the rendering thread
    app.taskMgr.setupTaskChain("speech_chain", numThreads=1)
    
    recognizer = sr.Recognizer()

    if not app.args.no_noise_calibration:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)

    generate_puzzle(app)

def generate_puzzle(app):
    global bytes_hex_strs
    global word

    # Generate the code
    puzzle_bytes, bytes_hex_strs = generate_code()
    # Analyze the code and determine the key
    word = analyze_code(puzzle_bytes)

    display_puzzle_hex(app, Puzzle.HOLD)
    display_puzzle_hex(app, Puzzle.LOCALIZATION)
    display_puzzle_hex(app, Puzzle.SEQUENCE)

def display_puzzle_hex(app, puzzle):
    if puzzle != Puzzle.WIRES:
        text_node = app.num_texts[int(puzzle)] 
        text_node.setText(bytes_hex_strs[int(puzzle)])

def focus(app):
    app.bomb.hprInterval(0.25, (0, 0, 0)).start()
    app.focused = Puzzle.SPEECH
    
    if not app.is_solved(Puzzle.SPEECH) and not app.taskMgr.hasTaskNamed("speech_chain"):
        task_state = {
            "app": app,
            "started": False,
        }

        app.taskMgr.add(__task_process_speech, extraArgs=[task_state], appendTask=True, taskChain="speech_chain")

def __set_status(status: Status):
    def handle_lights(on_nps, off_nps):
        on_status_np, on_light_np = on_nps
        off_status_np, off_light_np = off_nps

        on_status_np.setLight(on_light_np)
        off_status_np.setLightOff(off_light_np)

    match status:
        case Status.LISTENING:
            handle_lights(status_nps['blue'], status_nps['red'])
        case Status.IDLE:
            handle_lights(status_nps['red'], status_nps['blue'])
    
def __task_process_speech(task_state, task):
    app = task_state["app"]
    print(task_state['started'])
    if app.focused != Puzzle.SPEECH or not app.running:
        return task.done
    # Initialize the recognizer
    # Use the default microphone as the audio source
    if not task_state['started']:
        with sr.Microphone() as source:
            try:
                print("waiting on start")
                audio_start = recognizer.listen(source, timeout=5, phrase_time_limit=3)
            except Exception as e:
                print(e)
                return task.again
        try:
            print("tried")
            spoken_start = recognizer.recognize_google(audio_start)
            print(f'word: {spoken_start}')
            if "begin" not in spoken_start.lower().replace(" ", ""):
                print("not equal")
                return task.again
            else:
                task_state['started'] = True
                return task.again
        except Exception as e:
            print("exception")
            # Speech is unintelligible
            print(e)
            return task.again
    else:
        print("enter phrase")
        with sr.Microphone() as source:
            try:
                __set_status(Status.LISTENING)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)             
            except Exception as e:
                return task.again
        try:
            # Recognize speech using Google Speech Recognition
            # print("You said " + r.recognize_google(audio))    
            
            # Check if the recognized speech matches the key
            spoken = recognizer.recognize_google(audio)
            print(spoken)
            if word.lower() in spoken.lower().replace(" ", ""):
                app.taskMgr.add(app.solve_puzzle, extraArgs=[Puzzle.SPEECH])
                task_state["started"] = False
                __set_status(Status.IDLE)
                return task.done
            else:
                app.taskMgr.add(app.handle_mistake, extraArgs=[])
                # Use condition lock to wait for main thread to increment mistake counter
                app.mistakes_lock.wait()
                if app.mistakes < 3:
                    task_state["started"] = False
                    __set_status(Status.IDLE)
                    return task.again
                else:
                    task_state["started"] = False
                    __set_status(Status.IDLE)
                    return task.done
        
        except Exception as e:                            
            # Speech is unintelligible
            return task.again