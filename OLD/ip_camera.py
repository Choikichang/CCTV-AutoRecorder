import os
import cv2

# Change ip for your camera
cam_ip = "192.168.0.56"
id = "admin"
pw = "yonsei1!"
path_video = f"rtsp://{id}:{pw}@{cam_ip}/trackID=1"

cap = cv2.VideoCapture(path_video)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)

frame_count = 0
while cap.isOpened():

    ret, frame = cap.read()
    
    # Display the frame in a window
    # Resize is only performed for visualization
    resized_frame = cv2.resize(frame, (1600, 900))
    cv2.imshow('Camera Feed', resized_frame)
    frame_count += 1
    
    print(f"Frame count : {frame_count}", end='\r')

    # Press 'q' to exit the loop and close the window
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all windows
cap.release()