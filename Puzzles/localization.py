import numpy as np
import cv2
import random
import time


# Constants for the game
STAGE_COUNT = 4
COLORS = ['r','g','y','b']
COLOR_REPEAT_TABLE = {
    'r': {1: 4, 2: 4, 3: 2},
    'g': {1: 2, 2: 4, 3: 2},
    'y': {1: 1, 2: 1, 3: 3},
    'b': {1: 2, 2: 1, 3: 3}
}

# Initialize game variables
user_answer=[]
mistake=0
clue = 'd'

# Set up video capture
cap = cv2.VideoCapture(1)  # Start video capture
WIDTH = int(cap.get(3))  # Get video width
HEIGHT = int(cap.get(4))  # Get video height

# Define screen boundary constants for bomb movement
L_X_BOUND = int(WIDTH/4)
R_X_BOUND = int(3*WIDTH/4)
T_Y_BOUND = int(HEIGHT/3)
B_Y_BOUND = int(2*HEIGHT/3)
MARGIN_X = int(WIDTH/8)
MARGIN_Y = int(HEIGHT/9)


def generate_stages():
    """Generate a sequence of colors (stages) for the game."""
    stages = []
    for i in range(STAGE_COUNT):
        l_color = [COLORS[random.randint(0, 3)]] * random.randint(1, 3) # Random color, random repeats
        s_color = ''.join(l_color)
        stages.append(s_color)
    return stages

def generate_key(stages):
    """Generate the solution key based on the stages."""
    answer_key = []
    for pattern in stages:
        answer_key.append(COLOR_REPEAT_TABLE[pattern[0]][len(pattern)])
    return answer_key

# Generate game stages and solution key
stages = generate_stages()
answer_key = generate_key(stages)

# Game loop for each stage
for i_stage in range(STAGE_COUNT):
    print(f"The bomb shows the characters: {stages[i_stage]}")
    new_added = False
    centered = False
    while True:
        _, image = cap.read()
        image = cv2.flip(image, 1) # Flip the image for natural interaction
        cv2.imshow('image', image)

        # convert from BGR to HSV color space
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Define the color range for detection
        lower_limit = np.array([90, 200, 200])
        upper_limit = np.array([110, 255, 255])

        # Create a mask to detect objects within the color range
        mask = cv2.inRange(hsv_image, lower_limit, upper_limit)
        contours, hierarchy = cv2.findContours(mask, 1, 2) # Find contours in the mask

        # Draw rectangles to indicate different zones on the screen
        cv2.rectangle(image, (0, 0), (L_X_BOUND, T_Y_BOUND), (0, 0, 255),  1)
        cv2.rectangle(image, (R_X_BOUND, 0), (WIDTH, T_Y_BOUND), (0, 0, 255), 1)
        cv2.rectangle(image, (0, B_Y_BOUND), (L_X_BOUND, HEIGHT), (0, 0, 255), 1)
        cv2.rectangle(image, (R_X_BOUND, B_Y_BOUND), (WIDTH, HEIGHT), (0, 0, 255), 1)
        # Center rectangle
        cv2.rectangle(image, (L_X_BOUND + MARGIN_X, T_Y_BOUND), \
                      (R_X_BOUND-MARGIN_X, B_Y_BOUND), (0, 255, 0), 1)

        # Process the largest contour detected
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour) # Get bounding box of largest contour
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2) # Draw bounding box

            color_middle_x = x + w/2
            color_middle_y = y + h/2

            # Check if the object is centered within the designated area
            if color_middle_x <= R_X_BOUND - MARGIN_X and color_middle_x >= L_X_BOUND + MARGIN_X and \
                color_middle_y >= T_Y_BOUND and color_middle_y <= B_Y_BOUND:
                centered= True
            
            # Check the corner based on object position and add user's answer
            if centered:
                if color_middle_x < L_X_BOUND and color_middle_y < T_Y_BOUND:
                    user_answer.append(1)
                    new_added = True
                    centered= False
                elif color_middle_x > R_X_BOUND and color_middle_y < T_Y_BOUND:
                    user_answer.append(2)
                    new_added = True
                    centered= False
                elif color_middle_x < L_X_BOUND and color_middle_y > B_Y_BOUND:
                    user_answer.append(3)
                    new_added = True
                    centered= False
                elif color_middle_x > R_X_BOUND and color_middle_y > B_Y_BOUND:
                    user_answer.append(4)
                    new_added = True
                    centered= False
                
            # Validate user's answer with the answer key
            if new_added:
                new_added = False
                if user_answer[-1]!= answer_key[len(user_answer)-1]:
                    mistake += 1
                    print("Mistake!", mistake)
                    
                    user_answer = [] # Reset user answer for the current stage
                else:
                    if len(user_answer) != i_stage + 1:
                        print("Next position please!")
                    else:
                        user_answer = []  # Correct sequence for this stage, reset for the next stage
                        break # Move to the next stage

            # Check if the player has made too many mistakes
            if mistake >= 3:
                break
            # Check if the game is completed
            if len(user_answer) == len(answer_key):
                print("Success!")
                break

        cv2.imshow('image', image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Game over condition
    if mistake >= 3:
        print('BOOOOOOOM, BOMB HAS EXPLODED, YOU LOSE.')
        break

# Final message if the game is completed successfully
if mistake < 3:
    print('Congrats: that was correct.')
    print('Here is your next clue: ', clue)
    print('Switching to next game.')

cap.release()
cv2.destroyAllWindows()