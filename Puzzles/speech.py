import speech_recognition as sr
import random
import time

code = ''
key = ''


def generate_code():
    """Generate a code according to the given rules."""
    first_byte = random.randint(0, 255)  # Generate a random integer between 0 and 255 for the first byte
    second_byte = random.randint(0, 255)  # Generate a random integer between 0 and 255 for the second byte
    third_byte = random.randint(0, 255)  # Generate a random integer between 0 and 255 for the third byte

    # Convert integers to binary strings with leading zeros
    first_byte_binary = format(first_byte, '08b')
    second_byte_binary = format(second_byte, '08b')
    third_byte_binary = format(third_byte, '08b')

    # Concatenate binary strings to form the code
    code = first_byte_binary + ' ' + second_byte_binary + ' ' + third_byte_binary
    return code

def analyze_code():
    """Analyze the code and determine the output based on the given rules."""
    # Split the code into individual bytes
    bytes_list = code.split()

    # Check the conditions and determine the output
    if bytes_list[0][0] == '1':
        return "Grape"
    elif int(bytes_list[1], 2) % 8 == 0:
        return "Banana"
    elif bytes_list[2][-1] == '0':
        return "Apple"
    else:
        return "Dragonfruit"
    
def init():
    global code
    global key

    # Generate the code
    code = generate_code()
    # Analyze the code and determine the key
    key = analyze_code()

def game_loop(mistakes):
    first_speech = True
    # Main game loop
    while True:
        print("The bomb shows the following characters:", code)

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
                if str(spoken).lower().replace(" ", "") == key.lower():
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