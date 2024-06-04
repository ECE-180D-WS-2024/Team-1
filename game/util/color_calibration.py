
import cv2
import numpy as np

# Global variable to store the last 10 dominant HSV values
last_10_hsv_values = []

def get_dominant_color(frame, center, width, height):
    x, y = center
    x1, y1 = max(0, x - width//2), max(0, y - height//2)
    x2, y2 = min(frame.shape[1], x + width//2), min(frame.shape[0], y + height//2)
    
    cropped_frame = frame[y1:y2, x1:x2]
    hsv_frame = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2HSV)
    
    # Reshape the HSV image
    hsv_flat = hsv_frame.reshape((-1, 3))
    
    # Apply k-means clustering to find dominant colors
    k = 1  # Number of clusters
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, centers = cv2.kmeans(hsv_flat.astype(np.float32), k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    
    # Get the most dominant color (center of the cluster)
    dominant_color_hsv = np.uint8([[[centers[0][0], centers[0][1], centers[0][2]]]])
    
    return dominant_color_hsv

def calibration_loop():
    cap = cv2.VideoCapture(0)
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Failed to capture frame")
            break

        height, width = frame.shape[:2]
        border_thickness = 50
        width = width + 2*border_thickness  # Get video width
        height = height + 2*border_thickness  # Get video height
        center = (width // 2, height // 2)
        rect_width, rect_height = 100, 100

        frame = cv2.flip(frame, 1)  # Flip horizontally
        frame = cv2.copyMakeBorder(frame, border_thickness, border_thickness, border_thickness, border_thickness, cv2.BORDER_CONSTANT, value=(255, 255, 255))
        
        dominant_color_hsv = get_dominant_color(frame, center, rect_width, rect_height)
        
        # Append the dominant HSV value to the list
        last_10_hsv_values.append(dominant_color_hsv[0])
        
        # If the list contains 10 values, calculate the average and output it
        if len(last_10_hsv_values) == 10:
            average_hsv = np.mean(last_10_hsv_values, axis=0).astype(int)
            print(f'Average HSV value of last 10 frames: [{average_hsv[0][0]}, {average_hsv[0][1]}, {average_hsv[0][2]}]' )
            last_10_hsv_values.clear()  # Clear the list
            
        # Draw rectangle indicating region of interest
        cv2.rectangle(frame, (center[0] - rect_width//2, center[1] - rect_height//2),
                      (center[0] + rect_width//2, center[1] + rect_height//2), (0, 255, 0), 2)
        
        # Display the camera feed
        cv2.imshow('Camera Feed', frame)
        
        frame_count += 1
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    cap.release()
    return [average_hsv[0][0], average_hsv[0][1], average_hsv[0][2]]

def calibrate():
    print("Starting Color Calibration! Press q on camera feed when ready.")
    return calibration_loop()
