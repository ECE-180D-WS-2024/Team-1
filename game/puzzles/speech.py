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
    binary_bytes = [format(b, '08b') for b in bytes]

    # Split the code into individual bytes
    # Check the conditions and determine the output
    if binary_bytes[0][0] == '1':
        return "Orange"
    elif int(binary_bytes[1], 2) % 8 == 0:
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
        'green': setup_light('green', (0, 255, 0, 1)),
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
    
    app.taskMgr.add(__task_process_speech, extraArgs=[app], appendTask=True, taskChain="speech_chain")

def __set_status(status: Status):
    def handle_lights(on_nps, off_nps):
        on_status_np, on_light_np = on_nps
        off_status_np, off_light_np = off_nps

        on_status_np.setLight(on_light_np)
        off_status_np.setLightOff(off_light_np)

    match status:
        case Status.LISTENING:
            handle_lights(status_nps['green'], status_nps['red'])
        case Status.IDLE:
            handle_lights(status_nps['red'], status_nps['green'])
    
def __task_process_speech(app, task):
    if app.focused != Puzzle.SPEECH or not app.running:
        return task.done
    # Initialize the recognizer
    # Use the default microphone as the audio source
    with sr.Microphone() as source:
        try:
            print("waiting on start")
            audio_start = recognizer.listen(source, timeout=1, phrase_time_limit=1)
        except Exception as e:
            return task.again
    try:
        spoken_start = recognizer.recognize_google(audio_start)
        print(spoken_start)
        if str(spoken_start).lower().replace(" ", "") != "start":
            return task.again
        else:
            __set_status(Status.LISTENING)
    except Exception as e:
        # Speech is unintelligible
        return task.again
    
    with sr.Microphone() as source:
        try:
            audio = recognizer.listen(source, timeout=2, phrase_time_limit=1)             
            __set_status(Status.IDLE)      
        except Exception as e:
            return task.again
    try:
        # Recognize speech using Google Speech Recognition
        # print("You said " + r.recognize_google(audio))    
        
        # Check if the recognized speech matches the key
        print(spoken)
        spoken = recognizer.recognize_google(audio)
        if str(spoken).lower().replace(" ", "") == word.lower():
            app.taskMgr.add(app.solve_puzzle, extraArgs=[Puzzle.SPEECH])
            return task.done
        else:
            app.taskMgr.add(app.handle_mistake, extraArgs=[])
            # Use condition lock to wait for main thread to increment mistake counter
            app.mistakes_lock.wait()
            if app.mistakes < 3:
                return task.again
            else:
                return task.done
    
    except Exception as e:                            
        # Speech is unintelligible
        return task.again