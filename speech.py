import speech_recognition as sr
import random

mistake = 0  # Counter for mistakes made by the player
clue = 'c'  # Initial clue for the player

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

def analyze_code(code):
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

# Generate the code
code = generate_code()

# Analyze the code and determine the key
key = analyze_code(code)

# Main game loop
while True:
    print("The bomb shows the following characters:", code)

    print("Enter 0 to begin speech recognition.")
    x = int(input())
    if x!=0:
        break
    else:
        print("Begin Speaking:")

        # Initialize the recognizer
        r = sr.Recognizer()

        # Use the default microphone as the audio source
        with sr.Microphone() as source:                
            audio = r.listen(source)                   # listen for the first phrase and extract it into audio data

        try:
            # Recognize speech using Google Speech Recognition
            # print("You said " + r.recognize_google(audio))    
            
            # Check if the recognized speech matches the key
            if str(r.recognize_google(audio)).lower().replace(" ", "") == key.lower():
                print('Congrats: that was correct.')
                print('Here is your next clue: ', clue)
                print('Switching to next game.')
                break
            else:
                mistake += 1
                print('Wrong, Mistakes: ', mistake)
                # Check if the player has made too many mistakes
                if mistake >= 3:
                    print('BOOOOOOOM, BOMB HAS EXPLODED, YOU LOSE.')
                    break
                else:
                    print('Please Retry')
        
        except:                            
            # Speech is unintelligible
            print("Could not understand audio, please retry.")
