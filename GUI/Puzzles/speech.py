import speech_recognition as sr
import random
from puzzles import Puzzle

recognizer = None
bytes_hex_str = []
puzzle_bytes = []
word = ''


def generate_code():
    """Generate a code according to the given rules."""
    byte_key = [] # Ordering: 0 -> sequence, 1 -> wires, 2 -> localization, 3 -> hold

    # Generate 4 bytes
    for _ in range(4):
        byte_key.append(random.randint(0, 255))
    bytes_hex_strs = [format(b, '02X') for b in byte_key]

    return byte_key, bytes_hex_strs

def analyze_code(bytes):
    """Analyze the code and determine the output based on the given rules."""
    binary_bytes = [format(b, '08b') for b in bytes]

    # Split the code into individual bytes
    # Check the conditions and determine the output
    if binary_bytes[0][0] == '1':
        return "Grape"
    elif int(binary_bytes[1], 2) % 8 == 0:
        return "Banana"
    elif binary_bytes[2][-1] == '0':
        return "Apple"
    else:
        return "Dragonfruit"
    
def init(app):
    global recognizer
    global puzzle_bytes
    global word
    global bytes_hex_strs

    # Create task chain to allow speech recognition 
    # to run on a thread separate from the rendering thread
    app.taskMgr.setupTaskChain("speech_chain", numThreads=1)
    
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)

    # Generate the code
    puzzle_bytes, bytes_hex_strs = generate_code()
    # Analyze the code and determine the key
    word = analyze_code(puzzle_bytes)

def display_puzzle_hex(app, puzzle):
    text_node = app.num_texts[int(puzzle)]
    text_node.setText(bytes_hex_strs[int(puzzle)])

def focus(app):
    app.bomb.hprInterval(0.25, (0, 0, 0)).start()
    app.focused = Puzzle.SPEECH
    
    app.taskMgr.add(__task_process_speech, extraArgs=[app], appendTask=True, taskChain="speech_chain")

def __task_process_speech(app, task):
    if app.focused != Puzzle.SPEECH:
        return task.done
    # Initialize the recognizer
    # Use the default microphone as the audio source
    with sr.Microphone() as source:
        audio = recognizer.listen(source, timeout=3)                   
    try:
        # Recognize speech using Google Speech Recognition
        # print("You said " + r.recognize_google(audio))    
        
        # Check if the recognized speech matches the key
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