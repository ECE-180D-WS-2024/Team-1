import speech_recognition as sr
import random
import time

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
    
def init():
    global puzzle_bytes
    global word
    global bytes_hex_strs

    # Generate the code
    puzzle_bytes, bytes_hex_strs = generate_code()
    # Analyze the code and determine the key
    word = analyze_code(puzzle_bytes)

def display_puzzle_hex(app, puzzle):
    text_node = app.num_texts[int(puzzle)]
    text_node.setText(bytes_hex_strs[int(puzzle)])

def game_loop(mistakes):
    first_speech = True
    # Main game loop
    while True:
        print("The bomb shows the following characters:", puzzle_bytes)

        print("Enter 0 to begin speech recognition ('s' to switch puzzles): ")
        x = input()

        if x == 's':
            return False

        if int(x)!=0:
            break
        else:
            # Initialize the recognizer
            r = sr.Recognizer()
            # Use the default microphone as the audio source
            with sr.Microphone() as source:       
                r.adjust_for_ambient_noise(source)    
                if first_speech:
                    time.sleep(0.5)
                    first_speech = False
                print("Begin Speaking:")     
                audio = r.listen(source)                   # listen for the first phrase and extract it into audio data

            try:
                # Recognize speech using Google Speech Recognition
                # print("You said " + r.recognize_google(audio))    
                
                # Check if the recognized speech matches the key
                spoken = r.recognize_google(audio)
                if str(spoken).lower().replace(" ", "") == word.lower():
                    return True
                else:
                    mistakes[0] += 1
                    print('Wrong, Mistakes: ', mistakes[0])
                    # Check if the player has made too many mistakes
                    if mistakes[0] >= 3:
                        return False
            
            except Exception as e:                            
                # Speech is unintelligible
                print(e)
                print("Could not understand audio, please retry.")


def start_speech(mistakes):
    return game_loop(mistakes)