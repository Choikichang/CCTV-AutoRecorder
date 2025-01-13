import cv2
import numpy as np
from numba import jit
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget
import time
import os
from collections import deque
import sys

# MSE 계산 함수 (이미지 일부분만 비교하도록 수정)
@jit
def mse(imageA: np.ndarray, imageB: np.ndarray):
    h, w, _ = imageA.shape
    # 중앙 부분만 사용 (이미지 크기의 50%)
    roi_h, roi_w = h // 2, w // 2
    start_h, start_w = h // 4, w // 4
    regionA = imageA[start_h:start_h + roi_h, start_w:start_w + roi_w]
    regionB = imageB[start_h:start_h + roi_h, start_w:start_w + roi_w]

    err = np.sum((regionA.astype("float") - regionB.astype("float")) ** 2)
    err /= float(regionA.shape[0] * regionA.shape[1])
    return err

class CameraApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Camera IP Input")

        self.label = QLabel("Enter Camera IP:", self)
        self.line_edit = QLineEdit("192.168.135.208", self)
        self.button = QPushButton("Start Streaming", self)
        self.button.clicked.connect(self.start_streaming)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.button)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

        self.cam_ip = None
        self.previous_frame = None  # 이전 프레임 저장 변수
        self.mse_threshold = 1000  # MSE 임계값 (변화 감지 기준)
        self.recording = False
        self.current_video_writer = None

    def start_streaming(self):
        self.cam_ip = self.line_edit.text()
        if self.cam_ip:
            path_video = f"rtsp://admin:eugene0924!@{self.cam_ip}/trackID=1"
            self.capture_video(path_video)

    def capture_video(self, path_video):
        self.cap = cv2.VideoCapture(path_video)
        if not self.cap.isOpened():
            print("Failed to open camera stream.")
            return

        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to read frame.")
                    break

                    # 프레임 크기 조정
                frame = cv2.resize(frame, (640, int(640 * frame.shape[0] / frame.shape[1])))

                # MSE 계산을 통해 변화 감지
                if self.run_mse_check(frame):
                    print("Significant change detected. Starting recording.")
                    if not self.recording:
                        self.start_recording(frame)
                elif self.recording and not self.run_mse_check(frame):
                    print("MSE below threshold. Stopping recording.")
                    self.stop_recording()

                # 녹화 중이면 현재 프레임 저장
                if self.recording:
                    self.current_video_writer.write(frame)

                # 화면 출력
                cv2.imshow('IP Camera Stream', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            self.cap.release()
            if self.current_video_writer:
                self.current_video_writer.release()
            cv2.destroyAllWindows()

    def run_mse_check(self, frame):
        if self.previous_frame is None:
            self.previous_frame = frame
            return False  # 첫 프레임을 기준으로 설정

        # 현재 프레임과 기준 프레임 간 MSE 계산
        mse_value = mse(self.previous_frame, frame)

        print(f"MSE Value: {mse_value}")

        # MSE가 임계값 이상이면 변화 감지
        return mse_value > self.mse_threshold

    def start_recording(self, frame):
        self.recording = True
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        output_dir = 'C:\\Users\\User\\Desktop\\Eugene_Concrete_Slump_Video'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        self.video_file_path = os.path.join(output_dir, f'output_{timestamp}.avi')
        self.current_video_writer = cv2.VideoWriter(
            self.video_file_path,
            cv2.VideoWriter_fourcc(*'XVID'),
            30.0,
            (frame.shape[1], frame.shape[0])
        )
        print("Recording started.")

    def stop_recording(self):
        if self.recording and self.current_video_writer:
            self.current_video_writer.release()
            self.recording = False
            print("Recording stopped.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    camera_app = CameraApp()
    camera_app.show()
    sys.exit(app.exec_())
