# predict_pouring.py

import cv2
import numpy as np
import logging

# Set up logger
log = logging.getLogger('detect_pouring')
log.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
log.addHandler(console_handler)

class PouringDetector:
    def __init__(self, motion_threshold=0.5, buffer_frames=10):
        self.prev_frame = None
        self.motion_threshold = motion_threshold
        self.buffer_frames = buffer_frames
        self.buffer_count = 0
        self.motion_detected = False
        self.video_writer = None
        self.video_segment = []

    def detect_pouring(self, frame):
        try:
            next_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if self.prev_frame is None:
                self.prev_frame = next_frame
                return False  # 첫 프레임이므로 움직임이 없음

            # Calculate optical flow between the previous and current frame
            flow = cv2.calcOpticalFlowFarneback(self.prev_frame, next_frame, None, 0.5, 3, 9, 3, 5, 1.2, 0)

            # Calculate the magnitude and angle of the flow
            magnitude, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])

            # Check if the magnitude of the motion is above the threshold
            if np.mean(magnitude) > self.motion_threshold:
                self.motion_detected = True
                self.buffer_count = 0
                log.debug(f"Motion detected: magnitude = {np.mean(magnitude)}")
                print("Detect!")
                return True
            else:
                if self.motion_detected:
                    self.buffer_count += 1
                    if self.buffer_count >= self.buffer_frames:
                        self.motion_detected = False
                log.debug(f"Magnitude stats - Min: {np.min(magnitude)}, Max: {np.max(magnitude)}, Mean: {np.mean(magnitude)}")

                print("Undetect!")
                return False

        except Exception as e:
            log.error(f"Unexpected error in detect_pouring: {e}")
            return False

        finally:
            self.prev_frame = next_frame  # Update previous frame for the next call