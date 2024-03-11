import numpy as np
import cv2
import random
import time

key = [1, 2, 3, 4]
random.shuffle(key)
answer=[]
print(key)
mistake=0

new_added = False

interval = 1
start = time.time()

cap = cv2.VideoCapture(0)
width  = cap.get(3)  # float `width`
height = cap.get(4)  # float `height`
print(width, height)

while True:

    _, image = cap.read()
    cv2.imshow('image', image)

    if time.time() - start < interval:
        continue
    start = time.time()

    # convert from BGR to HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # lower and upper limits for the white color
    lower_limit = np.array([90, 200, 200])
    upper_limit = np.array([110, 255, 255])

    # create a mask for the specified color range
    mask = cv2.inRange(hsv_image, lower_limit, upper_limit)
    # get the bounding box from the mask image
    contours, hierarchy = cv2.findContours(mask, 1, 2)

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        color_middle_x = x + w/2
        color_middle_y = y + h/2

        print('color_x', color_middle_x)
        print('color_y', color_middle_y)

        if color_middle_x < width/4 and color_middle_y < height/3:
            answer.append(1)
            new_added = True
        elif color_middle_x > 3*width/4 and color_middle_y < height/3:
            answer.append(2)
            new_added = True
        elif color_middle_x < width/4 and color_middle_y > 2*height/3:
            answer.append(3)
            new_added = True
        elif color_middle_x > 3*width/4 and color_middle_y > 2*height/3:
            answer.append(4)
            new_added = True

        if new_added:
            new_added = False
            if answer[-1]!= key[len(answer)-1]:
                mistake += 1
                print("Mistake!", mistake)
                answer = []
            else:
                print("Next position please!", mistake)
        
        if mistake >= 3:
            break

        if len(answer) == len(key):
            print("Success!")
            break


    cv2.imshow('image', image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()