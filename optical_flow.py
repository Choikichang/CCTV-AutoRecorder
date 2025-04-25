import cv2
import numpy as np
import logging
import time  # time 모듈 추가

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
        
        # 기준 프레임 리셋을 위한 변수 추가
        self.last_reset_time = time.time()
        self.reset_interval = 30 * 60  # 30분(초 단위)
        
    def detect_pouring(self, frame):
        try:
            next_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 30분마다 prev_frame 리셋
            current_time = time.time()
            if current_time - self.last_reset_time >= self.reset_interval:
                self.prev_frame = None  # prev_frame을 None으로 설정하여 다음 줄에서 재초기화되도록 함
                self.last_reset_time = current_time
                log.info("Reference frame has been reset after 30 minutes")
            
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
